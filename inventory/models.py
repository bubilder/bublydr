from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

from accounts.models import User

class Unit(models.Model):
    """Одиниці виміру (кг, л, шт і т.д.)"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Назва'))
    short_name = models.CharField(max_length=10, unique=True, verbose_name=_('Скорочення'))
    
    class Meta:
        verbose_name = _('Одиниця виміру')
        verbose_name_plural = _('Одиниці виміру')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.short_name})"

class ProductCategory(models.Model):
    """Категорії продуктів (м'ясо, овочі, напої і т.д.)"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    
    class Meta:
        verbose_name = _('Категорія продуктів')
        verbose_name_plural = _('Категорії продуктів')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Продукт або інгредієнт"""
    
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name=_('Категорія')
    )
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.PROTECT, 
        related_name='products',
        verbose_name=_('Одиниця виміру')
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Ціна за одиницю'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Поточна кількість')
    )
    minimum_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Мінімальна кількість')
    )
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    barcode = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Штрих-код')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    
    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукти')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.current_quantity} {self.unit.short_name})"
    
    @property
    def is_low_stock(self):
        """Перевіряє, чи кількість продукту менша за мінімальну"""
        return self.current_quantity < self.minimum_quantity
    
    @property
    def total_value(self):
        """Повертає загальну вартість запасів цього продукту"""
        return self.current_quantity * self.price_per_unit
    
    @total_value.setter
    def total_value(self, value):
        pass  # Нічого не робити, просто ігнорувати

class Supplier(models.Model):
    """Постачальник продуктів"""
    
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    contact_person = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_('Контактна особа')
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_('Телефон')
    )
    email = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name=_('Email')
    )
    address = models.TextField(blank=True, null=True, verbose_name=_('Адреса'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    
    class Meta:
        verbose_name = _('Постачальник')
        verbose_name_plural = _('Постачальники')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    """Закупівля продуктів"""
    
    STATUS_CHOICES = (
        ('pending', 'Очікується'),
        ('ordered', 'Замовлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    )
    
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT, 
        related_name='purchases',
        verbose_name=_('Постачальник')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Статус')
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_purchases',
        verbose_name=_('Створив')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    ordered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата замовлення'))
    expected_delivery = models.DateField(null=True, blank=True, verbose_name=_('Очікувана доставка'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата доставки'))
    invoice_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Номер накладної')
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    
    class Meta:
        verbose_name = _('Закупівля')
        verbose_name_plural = _('Закупівлі')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Закупівля #{self.id} ({self.get_status_display()})"
    
    @property
    def total_amount(self):
        """Повертає загальну суму закупівлі"""
        return sum(item.total_price for item in self.items.all())
    
    def mark_as_ordered(self):
        """Позначити закупівлю як замовлену"""
        self.status = 'ordered'
        self.ordered_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Позначити закупівлю як доставлену і оновити запаси"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        
        # Оновлюємо кількість продуктів на складі
        for item in self.items.all():
            product = item.product
            product.current_quantity += item.quantity
            product.save()
        
        self.save()
    
    def mark_as_cancelled(self):
        """Позначити закупівлю як скасовану"""
        self.status = 'cancelled'
        self.save()

class PurchaseItem(models.Model):
    """Окремий продукт у закупівлі"""
    
    purchase = models.ForeignKey(
        Purchase, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('Закупівля')
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='purchase_items',
        verbose_name=_('Продукт')
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Кількість'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Ціна за одиницю'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    class Meta:
        verbose_name = _('Елемент закупівлі')
        verbose_name_plural = _('Елементи закупівлі')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        """Повертає загальну вартість елементу закупівлі"""
        return self.quantity * self.price_per_unit
    
    def save(self, *args, **kwargs):
        # Якщо ціна не встановлена, використовуємо поточну ціну продукту
        if not self.price_per_unit:
            self.price_per_unit = self.product.price_per_unit
        super().save(*args, **kwargs)

class Consumption(models.Model):
    """Списання продуктів"""
    
    REASON_CHOICES = (
        ('dish', 'Приготування страви'),
        ('waste', 'Списання (брак)'),
        ('inventory', 'Інвентаризація'),
        ('other', 'Інше'),
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='consumptions',
        verbose_name=_('Продукт')
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Кількість'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    reason = models.CharField(
        max_length=20, 
        choices=REASON_CHOICES, 
        default='other',
        verbose_name=_('Причина')
    )
    dish = models.ForeignKey(
        'menu.Dish', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='consumptions',
        verbose_name=_('Страва')
    )
    order_item = models.ForeignKey(
        'orders.OrderItem', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='consumptions',
        verbose_name=_('Елемент замовлення')
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_consumptions',
        verbose_name=_('Списав')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата списання'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    
    class Meta:
        verbose_name = _('Списання')
        verbose_name_plural = _('Списання')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity} {self.product.unit.short_name})"
    
    def save(self, *args, **kwargs):
        # Віднімаємо кількість від поточних запасів продукту
        product = self.product
        
        # Перевіряємо, чи це новий запис (перше збереження)
        is_new = self.pk is None
        
        if is_new:
            # Якщо це новий запис, зменшуємо кількість продукту
            product.current_quantity -= self.quantity
            product.save()
        else:
            # Якщо це оновлення існуючого запису, спочатку отримуємо старі дані
            old_instance = Consumption.objects.get(pk=self.pk)
            old_quantity = old_instance.quantity
            
            # Коригуємо кількість продукту з урахуванням зміни кількості списання
            quantity_diff = self.quantity - old_quantity
            product.current_quantity -= quantity_diff
            product.save()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Повертаємо кількість продукту при видаленні списання
        self.product.current_quantity += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)

class Recipe(models.Model):
    """Рецепт - зв'язок між стравою та інгредієнтами"""
    
    dish = models.OneToOneField(
        'menu.Dish', 
        on_delete=models.CASCADE, 
        related_name='recipe',
        verbose_name=_('Страва')
    )
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис приготування'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    
    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепти')
    
    def __str__(self):
        return f"Рецепт: {self.dish.name}"
    
    @property
    def ingredient_cost(self):
        """Розраховує собівартість страви на основі інгредієнтів"""
        return sum(item.cost for item in self.ingredients.all())

class RecipeIngredient(models.Model):
    """Інгредієнт у рецепті"""
    
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE, 
        related_name='ingredients',
        verbose_name=_('Рецепт')
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='recipe_usages',
        verbose_name=_('Продукт')
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Кількість'),
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    notes = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name=_('Примітки')
    )
    
    class Meta:
        verbose_name = _('Інгредієнт рецепту')
        verbose_name_plural = _('Інгредієнти рецепту')
        unique_together = ('recipe', 'product')
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity} {self.product.unit.short_name})"
    
    @property
    def cost(self):
        """Розраховує вартість цього інгредієнта для рецепту"""
        return self.quantity * self.product.price_per_unit