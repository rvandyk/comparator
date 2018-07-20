
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