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

    def available_quantity(self):
        """Розраховує максимальну кількість порцій страви, яку можна приготувати з наявних інгредієнтів"""
        try:
            # Перевіряємо, чи є рецепт для цієї страви
            recipe = self.recipe
            
            # Масимальна можлива кількість (початкове значення - дуже велике число)
            max_possible = float('inf')  # нескінченність
            
            # Для кожного інгредієнта в рецепті
            for recipe_ingredient in recipe.ingredients.all():
                product = recipe_ingredient.product
                required_per_dish = recipe_ingredient.quantity
                
                # Скільки порцій можна зробити з цього інгредієнта
                if required_per_dish > 0:  # уникаємо ділення на нуль
                    possible = product.current_quantity / required_per_dish
                else:
                    possible = float('inf')  # якщо інгредієнт не потрібен, то обмежень немає
                    
                # Знаходимо мінімальне можливе значення
                max_possible = min(max_possible, possible)
            
            # Округляємо до цілого числа вниз
            return int(max_possible)
        except Exception:
            # Якщо рецепту немає або виникла помилка
            return 999  # повертаємо велике число як "доступно багато"