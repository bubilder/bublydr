from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Категорія страв у меню (наприклад, перші страви, десерти, напої)"""
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name=_('Зображення'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    
    class Meta:
        verbose_name = _('Категорія')
        verbose_name_plural = _('Категорії')
        ordering = ['order']
        
    def __str__(self):
        return self.name
    
    @property
    def active_dishes(self):
        """Повертає всі активні страви в цій категорії"""
        return self.dishes.filter(is_available=True)

class Dish(models.Model):
    """Страва у меню ресторану"""
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Ціна'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes', verbose_name=_('Категорія'))
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name=_('Зображення'))
    is_available = models.BooleanField(default=True, verbose_name=_('В наявності'))
    preparation_time = models.PositiveIntegerField(default=15, help_text=_('Час приготування в хвилинах'), 
                                                  verbose_name=_('Час приготування'))
    
    # Інформація про інгредієнти для управління складом
    ingredients = models.ManyToManyField('inventory.Ingredient', through='DishIngredient', 
                                         related_name='dishes', verbose_name=_('Інгредієнти'))
    
    class Meta:
        verbose_name = _('Страва')
        verbose_name_plural = _('Страви')
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.price} грн)"
    
    def check_availability(self):
        """Перевіряє наявність інгредієнтів для страви"""
        for dish_ingredient in self.dishingredient_set.all():
            ingredient = dish_ingredient.ingredient
            required_amount = dish_ingredient.amount
            
            if ingredient.current_stock < required_amount:
                self.is_available = False
                self.save()
                return False
        
        self.is_available = True
        self.save()
        return True

class DishIngredient(models.Model):
    """Зв'язок між стравою та інгредієнтом"""
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name=_('Страва'))
    ingredient = models.ForeignKey('inventory.Ingredient', on_delete=models.CASCADE, verbose_name=_('Інгредієнт'))
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Кількість'))
    unit = models.CharField(max_length=20, verbose_name=_('Одиниця виміру'))
    
    class Meta:
        verbose_name = _('Інгредієнт страви')
        verbose_name_plural = _('Інгредієнти страв')
        unique_together = ('dish', 'ingredient')
        
    def __str__(self):
        return f"{self.ingredient.name} для {self.dish.name} ({self.amount} {self.unit})"