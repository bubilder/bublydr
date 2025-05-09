from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserLoginForm(AuthenticationForm):
    """Форма для авторизації користувача"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логін'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'password')

class UserRegistrationForm(UserCreationForm):
    """Форма для реєстрації нового користувача"""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім\'я'}),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Прізвище'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логін'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class UserProfileForm(UserChangeForm):
    """Форма для редагування профілю користувача"""
    password = None  # Виключаємо поле пароля з форми
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }