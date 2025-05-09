from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm

class UserLoginView(LoginView):
    """Авторизація користувача"""
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, _(f"Ласкаво просимо, {form.get_user().get_full_name()}!"))
        return super().form_valid(form)

class UserLogoutView(LogoutView):
    """Вихід користувача з системи"""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, _("Ви успішно вийшли з системи."))
        return super().dispatch(request, *args, **kwargs)

def is_admin(user):
    """Перевірка чи є користувач адміністратором"""
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

class StaffCreateView(UserPassesTestMixin, CreateView):
    """Створення нового персоналу (лише для адміністраторів)"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:staff_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, _("Користувача успішно створено"))
        return super().form_valid(form)

class StaffListView(UserPassesTestMixin, ListView):
    """Перегляд списку персоналу (лише для адміністраторів)"""
    model = User
    template_name = 'accounts/staff_list.html'
    context_object_name = 'staff'
    
    def test_func(self):
        return is_admin(self.request.user)

@login_required
def profile_view(request):
    """Перегляд і редагування профілю користувача"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Профіль успішно оновлено"))
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'accounts/profile.html', {'form': form})

@user_passes_test(is_admin)
def staff_delete_view(request, pk):
    """Видалення користувача (лише для адміністраторів)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, _("Користувача успішно видалено"))
        return redirect('accounts:staff_list')
        
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})