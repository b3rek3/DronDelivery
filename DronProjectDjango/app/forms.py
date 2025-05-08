from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
