![Pypi](https://img.shields.io/pypi/v/django-password-validator?style=flat-square) 
![Python](https://img.shields.io/pypi/pyversions/django-password-validator?style=flat-square)
![Django](https://img.shields.io/badge/Django-4.0%7C4.1%7C4.2%7C5.0-green)


# Django Password Validator

django-password-validator is a reusable app that provides a form field and
validators that check the strength of a password.

## Installation

You can install django-password-validator with pip by typing::

    pip install django-password-validator

Or with poetry by typing::

    poetry add django-password-validator

Or manually by downloading a tarball and typing::

    python setup.py install

## Settings

django-password-validator adds 6 optional settings

_Optional:_ 

#### Specifies minimum length for passwords:

```python
PASSWORD_MIN_LENGTH = 6 # Defaults to 6
```

#### Specifies maximum length for passwords:

```python
 PASSWORD_MAX_LENGTH = 120 # Defaults to None
```

#### Specifies the location of a dictionary (file with one word per line):

```python
PASSWORD_DICTIONARY = "/usr/share/dict/words" # Defaults to None
```

#### Specifies how close a fuzzy match has to be to be considered a match:

```python
PASSWORD_MATCH_THRESHOLD = 0.9 # Defaults to 0.9, should be 0.0 - 1.0 where 1.0 means exactly the same.
```

#### Specifies a list of common sequences to attempt to match a password against:

```python
PASSWORD_COMMON_SEQUENCES = [] # Should be a list of strings, see passwords/validators.py for default
```

#### Specifies number of characters within various sets that a password must contain:

```python
PASSWORD_COMPLEXITY = { # You can omit any or all of these for no limit for that particular set
            "UPPER": 1,     # Uppercase
            "LOWER": 1,     # Lowercase
            "LETTERS": 1,   # Either uppercase or lowercase letters
            "DIGITS": 1,    # Digits
            "SPECIAL": 1,   # Not alphanumeric, space or punctuation character
            "WORDS": 1      # Words (alphanumeric sequences separated by a whitespace or punctuation character)
        }
```

## Usage

To use the formfield simply import it and use it:

```python
from django import forms
from passwords.fields import PasswordField

class ExampleForm(forms.Form):
    password = PasswordField(label="Password")
```

You can make use of the validators on your own fields:

```python
from django import forms
from passwords.validators import dictionary_words

field = forms.CharField(validators=[dictionary_words])
```

You can also create custom validator instances to specify your own
field-specific configurations, rather than using the global
configurations:

```python
from django import forms
from passwords.validators import (DictionaryValidator, LengthValidator, ComplexityValidator)

field = forms.CharField(validators=[
    DictionaryValidator(words=['banned_word'], threshold=0.9),
    LengthValidator(min_length=8),
    ComplexityValidator(complexities=dict(
        UPPER=1,
        LOWER=1,
        DIGITS=1
    )),
])
```

Django's `password validation API` is slightly different than the form
validation API and has wrappers in the `auth_password_validators` module:

```python
AUTH_PASSWORD_VALIDATORS = [
        …,
        {"NAME": "passwords.auth_password_validators.ComplexityValidator"}
    ]
```

`password validation API`: https://docs.djangoproject.com/en/5.0/topics/auth/passwords/#module-django.contrib.auth.password_validation