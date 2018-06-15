from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json
from django.core.validators import URLValidator




def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True

def is_valid_json(jsonfile):
    try :
        json.loads(jsonfile)
    except ValueError as e:
        return False

    return True

def validate_xpath(value):
    if (not is_valid_json(value)):    
        raise ValidationError(
            _('Invalid JSON format'),
            params={'value': value},
        )
    elif not 'title' in json.loads(value) or not 'price' in json.loads(value):
        raise ValidationError(
            _('XPath needs fields title and price'),
            params={'value': value},
        )
    
def validate_url(value):
    if not is_valid_url(value):
        raise ValidationError(
            _('Invalid URL'),
            params={'value': value},
        )

class CrawlForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}),label='Crawler Name', max_length=100)
    url = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}), label='URL', max_length=100, validators=[validate_url])
    xpath = forms.CharField(label='JSON Xpath', widget=forms.Textarea(attrs={'class' : 'form-control', 'rows' : '3'}), validators=[validate_xpath])

    