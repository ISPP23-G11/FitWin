from django import forms

from .models import User


class EditProfileForm(forms.ModelForm):
    picture = forms.ImageField(label='Profile Picture',required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    birthday = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(max_length=260, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('picture','birthday','bio')

class UserUpdateForm(forms.ModelForm):
    first_name=forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name=forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
