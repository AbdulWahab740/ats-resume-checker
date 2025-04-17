from django import forms

class UploadFileForm(forms.Form):
    resume = forms.FileField()