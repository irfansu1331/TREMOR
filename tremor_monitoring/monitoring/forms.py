from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'login-input',
            'placeholder': 'Masukkan username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'login-input',
            'placeholder': 'Masukkan password',
            'autocomplete': 'current-password'
        })
    )
