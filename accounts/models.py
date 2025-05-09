from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Власний менеджер користувачів для наших потреб"""
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email є обов\'язковим полем')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """Розширена модель користувача з додатковими полями для ресторану"""
    
    ROLE_CHOICES = (
        ('ADMIN', 'Адміністратор'),
        ('WAITER', 'Офіціант'),
        ('CHEF', 'Шеф-кухар'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='WAITER', verbose_name=_('Роль'))
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Телефон'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Аватар'))
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('Користувач')
        verbose_name_plural = _('Користувачі')

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"