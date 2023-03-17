from django import forms
from .models import Trainer, Client
from django.contrib.auth.models import User

class EditProfileForm(forms.ModelForm):
    
    picture = forms.ImageField(label='Profile Picture',required=False, widget=forms.FileInput)
    birthday = forms.DateField(required=False)
    bio = forms.CharField(max_length=260, required=False)
    

    class Meta:
        model = Trainer
        fields = ('picture','birthday','bio')
        




class UserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name']