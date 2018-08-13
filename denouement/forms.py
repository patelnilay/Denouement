from django import forms
from django.contrib.auth.models import User

class SignInForm(forms.Form):
    username = forms.CharField(max_length=User._meta.get_field('username').max_length,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    password = forms.CharField(max_length=User._meta.get_field('password').max_length,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=User._meta.get_field('username').max_length,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    password = forms.CharField(max_length=User._meta.get_field('password').max_length,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )   
    )
    email = forms.CharField(widget=forms.EmailInput(
        attrs={
            'class': 'form-control'
        }
    ))

class ImageForm(forms.Form):
    image = forms.ImageField()