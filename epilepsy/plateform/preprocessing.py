import os
from os import path as path
from os import listdir as listd
from os.path import isfile,join
import pprint
import mne 
import pandas as pd
import numpy as np
import numpy as np
from mne.preprocessing import ICA
from django.shortcuts import render,redirect
from .models import Edf,Ica_image
from django.conf import settings
from django.core.files import File as DjangoFile
from django.http.response import HttpResponse



#Function to list a file name of directory in a list
def list_files_folder(folder_path,output=False):
    pp = pprint.PrettyPrinter()
    file_list = []

    for filename in listd(folder_path):
        if isfile(join(folder_path,filename)):
            file_list.append(filename)

    file_list.sort()

    if output==True:
        print(str(len(file_list)) + ' files found')
        pp.pprint(filename)

    return file_list


# Function to return df which content essential egg informations
def df_info(data,edfDic,typeOf,basePath):
    nomList = ['name','nchan','highpass','lowpass','sfreq','link']
    df = pd.DataFrame(columns=nomList)

    for i in range(1,len(data)):
    #for i in range(1,3):
        edf = path.join(basePath,typeOf,edfDic[typeOf][i])
        raw = mne.io.read_raw_edf(edf)
        dic={'name':edfDic[typeOf][i].split('.')[0],'nchan':raw.info['nchan'],'highpass':raw.info['highpass'],'lowpass':raw.info['lowpass'],'sfreq':raw.info['sfreq'],'link':edf}
        df = df.append(dic,ignore_index=True)

    return df

# list all no EEG signal in a raw
def list_no_EEG(raw):
    liste = []
    for f in raw.info['ch_names']:
        if 'EEG' not in f:
            liste.append(f)
    return liste

# remove bad channel
def remove_bad_channel(raw,info=False):
    real_bad_list = []
    del_chan = 0
    #a list of no common chanel
    liste = ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
       '31', '32', 'A1', 'A2', 'BURSTS', 'C3P', 'C4P', 'DC1-DC', 'DC2-DC',
       'DC3-DC', 'DC4-DC', 'DC5-DC', 'DC6-DC', 'DC7-DC', 'DC8-DC',
       'EDFANNOTATIONS', 'EKG', 'EKG1', 'EMG', 'IBI', 'LOC', 'LUC', 'OZ',
       'PG1', 'PG2', 'PHOTIC', 'RLC', 'ROC', 'SP1', 'SP2',
       'SUPPR', 'T1', 'T2']
    
    for i in range(len(raw.info['ch_names'])):
        for j in liste:
            if j in raw.info['ch_names'][i]:
                real_bad_list.append(raw.info['ch_names'][i])
                del_chan = del_chan+1
                if info:
                    print('I will delete ',raw.info['ch_names'][i],' channel')
    raw.drop_channels(real_bad_list)
    print(str(del_chan),' Channels deleted')

def replaceChar(string,replace,by,pos):
    final=""
    position = False
    for i in range(len(string)):
        if string[i]==replace and pos == i:
            position = True
    if position:
        for i in range(len(string)):
            if string[i]==replace and pos == i:
                final = final+by
            else:
                final = final+string[i]
        return final
    return string

def replace_diff(x):
  string = x.replace("-REF","").replace("-LE","").replace("EEG","").replace(" ","").replace("Z","z")
  return replaceChar(string, 'P', 'p', 1)



def change_channel_name(raw,info=False):
    raw_to=raw
    for i in range(len(raw_to.info['ch_names'])):
        raw.rename_channels({raw_to.info['ch_names'][i]:replace_diff(raw_to.info['ch_names'][i])})
    return raw_to




def transform_virtual_eeg_df(raw, selected_channels=[]):

    try:
        # use the reader to get an EdfReader file
        f = raw

        # get the names of the signals
        channel_names = f.getSignalLabels()
        # get the sampling frequencies of each signal
        channel_freq = f.getSampleFrequencies()
        
        # get a list of the EEG channels
        if len(selected_channels) == 0:
            selected_channels = channel_names

        # make an empty file of 0's
        sigbufs = np.zeros((f.getNSamples()[0],len(selected_channels)))
        # for each of the channels in the selected channels
        for i, channel in enumerate(selected_channels):
            try:
              # add the channel data into the array
              sigbufs[:, i] = f.readSignal(channel_names.index(channel))
            
            except:
              ValueError
              # This happens if the sampling rate of that channel is 
              # different to the others.
              # For simplicity, in this case we just make it na.
              sigbufs[:, i] = np.nan


        # turn to a pandas df and save a little space
        df = pd.DataFrame(sigbufs, columns = selected_channels)#.astype('float32')

        # get equally increasing numbers upto the length of the data depending
        # on the length of the data divided by the sampling frequency
        index_increase = np.linspace(0,
                                      len(df)/channel_freq[0],
                                      len(df), endpoint=False)

        # round these to the lowest nearest decimal to get the seconds
        #seconds = np.floor(index_increase).astype('uint16')

        seconds = index_increase
        
        # make a column the timestamp
        df['Time'] = seconds

        # make the time stamp the index
        df = df.set_index('Time')

        # name the columns as channel
        df.columns.name = 'Channel'

        return df, channel_freq[0]

    except:
        OSError
        return pd.DataFrame(), None
    


## For filtering
def filter_edf(filename,l_freq,h_freq,plt=False):
    raw = mne.io.read_raw_edf(filename,preload=True)
    remove_bad_channel(raw)
    raw =change_channel_name(raw,info=False)
    raw1 = raw

    if plt:
        print('before filtering')
        fig=raw.plot()
    #Filtering
    sfreq = raw.info['sfreq']
    l_freq = l_freq # we remove Delta Bande which probabily come from external noise
    h_freq = h_freq # Gamma bande
    method = 'fir'
    fir_design = 'firwin2'

    filter_param =  mne.filter.create_filter(raw.get_data(),
    sfreq=sfreq,l_freq=l_freq,h_freq=h_freq,method=method,fir_design=fir_design)
    filter_data = raw.filter(l_freq, h_freq,
                            method=method, 
                            fir_design=fir_design)
    picks_eeg = mne.pick_types(filter_data.info, meg=False, eeg=True, eog=False,
                            stim=False, exclude='bads')
    if plt:
        print('after filtering')
        fig=filter_data.plot()

    return filter_data,filter_param,raw1

def data_engineering_ica(raw,n_components,plt=False,nProperties=1):
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage,on_missing="ignore")
    raw.set_montage(montage)
    n_components = n_components  # if float, select n_components by explained variance of PCA

    #set components equal to number of channels

    method = 'infomax'  
    decim = 3  # we need sufficient statistics, not all time points -> saves time

    # we will also set state of the random number generator - ICA is a
    # non-deterministic algorithm, but we want to have the same decomposition
    # and the same order of components each time this tutorial is run
    random_state = 97

    ica = ICA(n_components=n_components, method=method, random_state=random_state)

    reject = dict(eeg=400e-6)

    picks_eeg = mne.pick_types(raw.info, meg=False, eeg=True, eog=False,
                           stim=False, exclude='bads')

    ica.fit(raw, picks=picks_eeg, decim=decim, reject=reject)

    if plt:
        print('ICA plot')
        figSource=ica.plot_sources(raw, show_scrollbars=False)
        print('Plot ICA Overlay to verify artifact correction')
        overplay = ica.plot_overlay(raw, exclude=[0], picks='eeg')
        print('Plot ICA Source')
        figComp=ica.plot_sources(raw, show_scrollbars=False)
        print('Plot ICA Properties')
        ica.plot_properties(raw, picks=range(nProperties))
        

    return ica

def missingPointFile(request):
    return render(request,'plateform/missingPointFile.html')

def preprocessing(request,pk):
    base = settings.BASE_DIR
    edf = Edf.objects.get(pk=pk)

    if Ica_image.objects.all().filter(edf=edf):
        ica_image = Ica_image.objects.get(edf=edf)
    else:
        try:
            filter_data,filter_param,raw = filter_edf(join(base,edf.edf.url.split('/')[1],edf.edf.url.split('/')[2],edf.edf.url.split('/')[3]),2,50)
            ica = data_engineering_ica(filter_data,19)

            #montage for selected channel
            montage = mne.channels.make_standard_montage('standard_1020')
            montage_plot=raw.set_montage(montage)
            image_montage = montage_plot.plot(show=False)

            

            num = []
            for i in range(19):
                num.append(i)
            
            
            ica_plt = ica.plot_components(picks=num,outlines='skirt',show=False)
            ica_properties = ica.plot_properties(inst=filter_data,show=False,picks=num)
            raw_plot = raw.plot(show=False)
            raw_filter_plot = filter_data.plot(show=False)

            #sensors and psd
            myPltFsensor=filter_data.plot_sensors(show_names=True,show=False)
            #plot spectral density
            myPltFpsd=filter_data.plot_psd(fmin=2, fmax=50,picks='eeg',show=False)

            myPltFsensor.savefig(edf.patient+'sensor.png')
            myPltFpsd.savefig(edf.patient+'psd.png')
            ica_plt.savefig(edf.patient+'.png')
            raw_plot.savefig(edf.patient+'1.png')
            raw_filter_plot.savefig(edf.patient+'2.png')
            ica_properties[17].savefig(edf.patient+'cz.png')

            image = DjangoFile(open(edf.patient+'.png', mode='rb'), name=edf.patient+'.png')
            image1 = DjangoFile(open(edf.patient+'1.png', mode='rb'), name=edf.patient+'1.png')
            image2 = DjangoFile(open(edf.patient+'2.png', mode='rb'), name=edf.patient+'2.png')
            image3 = DjangoFile(open(edf.patient+'sensor.png', mode='rb'), name=edf.patient+'sensor.png')
            image4 = DjangoFile(open(edf.patient+'psd.png', mode='rb'), name=edf.patient+'psd.png')
            image5 = DjangoFile(open(edf.patient+'cz.png', mode='rb'), name=edf.patient+'cz.png')


            ica_image = Ica_image.objects.create(edf=edf,ica_image=image,egg_mne=image1,
            egg_mne_filter=image2,psd=image4,sensors=image3,cz_propertie = image5)
            ica_image.save()

            image.close()
            image1.close()
            image2.close()
            image3.close()
            image4.close()
            image5.close()

            os.remove(edf.patient+'.png')
            os.remove(edf.patient+'1.png')
            os.remove(edf.patient+'2.png')
            os.remove(edf.patient+'sensor.png')
            os.remove(edf.patient+'psd.png')
            os.remove(edf.patient+'cz.png')
        except :
            return redirect('missing_point_file')


    context = {
        'doctor':edf.doctor,
        'patient':edf.patient,
        'ica_plt':ica_image.ica_image.url,
        'eeg':ica_image.egg_mne.url,
        'eeg_filter':ica_image.egg_mne_filter.url,
        'psd':ica_image.psd.url,
        'sensor':ica_image.sensors.url,
        'cz_propertie':ica_image.cz_propertie.url
    }

    return render(request,'plateform/expert_explore.html',context)