from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Форма для створення нового користувача з додатковими полями"""
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 
                  'phone', 'address', 'profile_image', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomAuthenticationForm(AuthenticationForm):
    """Форма для входу з покращеним стилем"""
    
    username = forms.CharField(
        label=_("Логін"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введіть логін')})
    )
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введіть пароль')})
    )

class UserProfileForm(forms.ModelForm):
    """Форма для редагування профілю користувача"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'profile_image')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'