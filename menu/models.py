from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Категорія страв у меню (наприклад: перші страви, десерти, напої)"""
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('Зображення'))
    order = models.IntegerField(default=0, verbose_name=_('Порядок відображення'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    
    class Meta:
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
        
    @property
    def active_dishes(self):
        """Повертає список активних страв у цій категорії"""
        return self.dishes.filter(is_available=True)

class Dish(models.Model):
    """Страва у меню ресторану"""
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Ціна'))
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name=_('Зображення'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes',
                                verbose_name=_('Категорія'))
    is_available = models.BooleanField(default=True, verbose_name=_('Доступна'))
    preparation_time = models.IntegerField(default=15, verbose_name=_('Час приготування (хв)'))
    is_vegetarian = models.BooleanField(default=False, verbose_name=_('Вегетаріанська'))
    is_spicy = models.BooleanField(default=False, verbose_name=_('Гостра'))
    
    class Meta:
        verbose_name = _('Страва')
        verbose_name_plural = _('Страви')
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name