from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Account

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nazwa użytkownika'
        })
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hasło'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nazwa użytkownika'
        })
    )
    password1 = forms.CharField(
        label='Hasło',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hasło'
        })
    )
    password2 = forms.CharField(
        label='Potwierdzenie hasła',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Powtórz hasło'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa konta (np. Portfel, Konto bankowe)'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }