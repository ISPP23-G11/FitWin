from django import forms

class FormMessages(forms.Form):
    message=forms.CharField(widget=forms.Textarea(attrs={

        "class": "form_ms",
        "placeholder": "Escriba su mensaje"
    }))