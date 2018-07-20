from django import forms
from django.utils.translation import gettext_lazy as _
from mainapp.validators import validate_url, validate_xpath






class CrawlForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}),label='Crawler Name', max_length=100)
    url = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}), label='URL', max_length=100, validators=[validate_url])
    xpath = forms.CharField(label='JSON Xpath', widget=forms.Textarea(attrs={'class' : 'form-control', 'rows' : '3'}), validators=[validate_xpath])

    