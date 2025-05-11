from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm

class CustomLoginView(LoginView):
    """Сторінка входу з кастомною формою"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    """Вихід з системи"""
    next_page = reverse_lazy('accounts:login')

@login_required
def profile_view(request):
    """Відображення профілю користувача"""
    return render(request, 'accounts/profile.html', {'user': request.user})

class RegisterUserView(SuccessMessageMixin, CreateView):
    """Реєстрація нового користувача (тільки для адміністраторів)"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:users_list')
    success_message = _("Користувача успішно створено!")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

class UpdateProfileView(SuccessMessageMixin, UpdateView):
    """Редагування профілю користувача"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Профіль успішно оновлено!")
    
    def get_object(self, queryset=None):
        return self.request.user

@login_required
def users_list_view(request):
    """Список всіх користувачів (тільки для адміністраторів)"""
    if not request.user.is_admin:
        return redirect('accounts:profile')
    
    users = User.objects.all().order_by('user_type', 'username')
    return render(request, 'accounts/users_list.html', {'users': users})