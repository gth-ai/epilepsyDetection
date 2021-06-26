from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    STATUS = (
        ('patient','patient'),
        ('expert','expert')
    )

    user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    lastname = models.CharField(max_length=100,null=True)
    firstname = models.CharField(max_length=100,null=True)
    email = models.CharField(max_length=100,null=True)
    phone = models.CharField(max_length=20,null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    status = models.CharField(max_length=100,null=True,choices=STATUS)
    


    def __str__(self):
        return self.firstname


class Edf(models.Model):
    DECISION = (
        ('epilepsy','Epileptic'),
        ('no_epilepsy','No Epileptic')
    )
    patient = models.CharField(max_length=100)
    doctor = models.CharField(max_length=100)
    saveBy = models.ForeignKey(Customer,null=True,on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    edf = models.FileField(upload_to='edfs/',null=True,blank=True)
    decision = models.CharField(max_length=100,null=True,choices=DECISION)

    def __str__(self):
        return self.patient

class Ica_image(models.Model):
    edf = models.ForeignKey(Edf,null=True,on_delete=models.SET_NULL)
    ica_image = models.FileField(upload_to='ica/')
    egg_mne = models.FileField(upload_to='eeg/',null=True,blank=True)
    egg_mne_filter = models.FileField(upload_to='eeg_filter/',null=True,blank=True)
    psd = models.FileField(upload_to='psd/',null=True,blank=True)
    sensors = models.FileField(upload_to='sensors/',null=True,blank=True)
    cz_propertie = models.FileField(upload_to='cz_properties/',null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)

    
