from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets


from .models import Edf,Customer

class Edfform(forms.ModelForm):
    class Meta:
        model = Edf
        fields = ('patient','doctor','edf')

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        widgets = {
            'username':forms.TextInput(attrs={
                'class':'form-control form-control-user',
                'placeholder':'User Name'
                }),
            'email':forms.EmailInput(attrs={
                'class':'form-control form-control-user',
                'placeholder':'Email'
                }),
            'password1':forms.PasswordInput(attrs={
                'class':'form-control form-control-user',
                'placeholder':'Password'
                }),
            'password2':forms.PasswordInput(attrs={
                'class':'form-control form-control-user',
                'placeholder':'Repeat Password'
                })
        }

class Customerform(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user','status']
