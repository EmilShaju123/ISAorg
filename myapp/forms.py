from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class transporterform(forms.Form):
    trans=forms.CharField(max_length=20)

class partyform(forms.Form):
    party=forms.CharField(max_length=20)
    add=forms.CharField(max_length=50)

class placeform(forms.Form):
    place=forms.CharField(max_length=20)

class logform(forms.Form):
    uname=forms.CharField(max_length=20)
    pas=forms.CharField(max_length=20)

