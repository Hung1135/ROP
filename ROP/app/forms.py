from django import forms

class UploadCVForm(forms.Form):
    file = forms.FileField()
