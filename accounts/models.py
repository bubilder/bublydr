from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Користувацька модель користувача з додатковими полями"""
    
    USER_TYPE_CHOICES = (
        ('admin', 'Адміністратор'),
        ('manager', 'Менеджер'),
        ('waiter', 'Офіціант'),
        ('cook', 'Кухар'),
        ('cashier', 'Касир'),
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='waiter',
        verbose_name=_('Тип користувача')
    )
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Номер телефону'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Адреса'))
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name=_('Фото профілю')
    )
    
    class Meta:
        verbose_name = _('Користувач')
        verbose_name_plural = _('Користувачі')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin' or self.is_staff
    
    @property
    def is_waiter(self):
        return self.user_type == 'waiter'
    
    @property
    def is_cook(self):
        return self.user_type == 'cook'
    
    @property
    def is_cashier(self):
        return self.user_type == 'cashier'
    
    @property
    def is_manager(self):
        return self.user_type == 'manager'