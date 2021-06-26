from tensorflow.keras import models
import uuid
import pandas as pd
import os
import tensorflow as tf
import mne
from sklearn.preprocessing import MinMaxScaler,LabelEncoder
import numpy as np
import librosa as lib
from .models import Edf
from django.shortcuts import render
from django.conf import settings



import logging
tf.get_logger().setLevel(logging.ERROR)


def get_label(file_path):
      return tf.strings.split(file_path,os.path.sep)[-2]
def get_data_label2(file_names):
  scaler = MinMaxScaler()
  encoder = LabelEncoder()
  data = []
  labels = []
  for i,path in enumerate(file_names):
    label = tf.compat.as_str(
      get_label(path).numpy(), encoding='utf-8')
    raw = pd.read_csv(path)
    nd=[]
    print(i)
    if 'Unnamed: 0' in list(raw.columns):
      raw.drop("Unnamed: 0",axis=1,inplace=True,errors="ignore")
      raw.to_csv(path,index=False)

    for col in raw.columns:
      
      #filteredSig=passBandFilter(raw[col])
      #spect = lib.feature.mfcc(np.array(filteredSig),n_mfcc=20)
      spect = tf.signal.stft(list(raw[col]), frame_length=255, frame_step=128,)
      spect = tf.abs(tf.dtypes.cast(spect, tf.float64))
      nd.append(lib.amplitude_to_db(spect.numpy()))
      
    nd=np.transpose(nd, (1, 2, 0))
    raw = tf.convert_to_tensor(nd/nd.max())
    data.append(raw)
    labels.append(label)
  labels=np.array(encoder.fit_transform(labels))# 
  print(labels)

  return (data,labels)

def divide_file(data_file,threshold,p,nb_cols=19):
  cols = [str(i) for i in range((nb_cols))]
  div=pd.DataFrame([],columns=cols)

  for j, path in enumerate(data_file["path"]):
    temp = pd.read_csv(path)
      
    n_cols = len((temp.columns))
    if n_cols > nb_cols:
      to_drop = temp.columns[nb_cols:]
      temp.drop(to_drop,axis=1,inplace=True)
      
    else :
      rest = nb_cols - n_cols
      rembourrage = np.zeros((threshold,1))
      for i in range(rest):
        temp[i]=rembourrage
        
    if len(temp.columns)!=nb_cols:
      print("anomalie : "+str(temp.columns)+" colonnes")
      print(path)
      return
    temp.columns = cols#div.columns
    div = pd.concat([div,temp])

    if div.shape[0]>threshold:
      nb_div = div.shape[0]//threshold
      file_name = path.split(os.path.sep)[-1][:-4] 
      for i in range(1,nb_div+1):
        new_path = p+file_name+"_"+str(i)+".csv"
        if not os.path.isfile(new_path):
          div[:threshold].to_csv(new_path,index=False)
        div=div[(threshold):]
        #print(div.shape)
      print(str(j))
    if j+1==len(data_file["path"]) and div.shape[0]<threshold and not div.empty:
      rest = threshold - div.shape[0]
      dd = pd.DataFrame(np.zeros((rest,len(div.columns))),columns=div.columns)
      div = pd.concat([div,dd])
      new_path = p+str(uuid.uuid1())+".csv"
      if div.shape[0]!=threshold:
        print("anomalie : "+str(div.shape[0])+" lignes")
        print(path)
        return
      div.to_csv(new_path,index=False)
      print("reste",div.shape)

def preprocessing_edf(root,edf_files=[],id=str(uuid.uuid1())):
  data_file = pd.DataFrame([],columns=["length","width","path","columns"])

  #dir = root+'/prod'+os.path.sep+id+os.path.sep
  dir = os.path.join(root,'prod','id')
  tf.io.gfile.makedirs(dir)
  for path in edf_files:
    file_name = path.split(os.path.sep)[-1][:-4]
    new_path = dir+os.path.sep+file_name+".csv"
    
    if not os.path.isfile(new_path):
      raw = mne.io.read_raw_edf(path)
      df = pd.DataFrame(raw.to_data_frame(),columns=raw.ch_names)
      data_file = data_file.append({"length":df.shape[0],"width":df.shape[1],"path":new_path,"columns":list(df.columns)}, ignore_index=True)
      df.to_csv(new_path,index=False)
  
  #suppresion des edf

  threshold=40000
  # division
  divide_file(data_file,threshold,dir)

  #suppression des csv
  for path in data_file["path"]:
    os.remove(path)

  print(dir[:-1])
  csv_names = tf.io.gfile.glob(str(dir) + '*.csv')

  return csv_names
  

def prediction(data_set):
  root = settings.BASE_DIR
  modele = models.load_model(os.path.join(root,'plateform','my_model.h5'))
  preds = modele.predict_classes(data_set)
  score = {"epilepsy": 0,"no_epilepsy": 0}
  for pred in preds:
    if pred == 0:
      score["epilepsy"]+=1
    else:
      score["no_epilepsy"]+=1
  print("predictions :", preds)
  print("score :", score)
  return  max(score, key=lambda k: score[k])

def make_prediction(request,pk):
  root = settings.BASE_DIR
  edf = Edf.objects.get(id=pk)
  edf_file_url = os.path.join(root,edf.edf.url.split('/')[1],edf.edf.url.split('/')[2],edf.edf.url.split('/')[3])
  decision = ''

  if edf.decision:
    decision = edf.decision
  else:
    csv_test_files = preprocessing_edf(root,[edf_file_url])
    test = tf.data.Dataset.from_tensor_slices(get_data_label2(csv_test_files))
    decision = prediction(test)
    Edf.objects.filter(id=pk).update(decision = decision)

  context = {
    'name':edf.patient,
    'decision': decision
  }

  return render(request,'plateform/decision.html',context)