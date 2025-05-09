from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal

class Order(models.Model):
    """Модель замовлення в ресторані"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Очікує обробки'),
        ('IN_PROGRESS', 'Готується'),
        ('READY', 'Готово до подачі'),
        ('DELIVERED', 'Подано'),
        ('COMPLETED', 'Завершено'),
        ('CANCELED', 'Скасовано'),
    )
    
    table = models.ForeignKey('tables.Table', on_delete=models.PROTECT, related_name='orders',
                             verbose_name=_('Стіл'))
    waiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders',
                              verbose_name=_('Офіціант'))
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING',
                             verbose_name=_('Статус'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    
    # Поля для оплати
    is_paid = models.BooleanField(default=False, verbose_name=_('Оплачено'))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                  verbose_name=_('Знижка %'))
    
    class Meta:
        verbose_name = _('Замовлення')
        verbose_name_plural = _('Замовлення')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Замовлення #{self.id} - {self.table}"
    
    @property
    def total_price(self):
        """Обчислення загальної вартості замовлення з урахуванням знижки"""
        subtotal = sum(item.total_price for item in self.items.all())
        discount_amount = subtotal * (self.discount / Decimal('100.0'))
        return subtotal - discount_amount
    
    @property
    def subtotal_price(self):
        """Обчислення вартості замовлення без знижки"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def discount_amount(self):
        """Обчислення суми знижки"""
        return self.subtotal_price * (self.discount / Decimal('100.0'))
    
    def add_item(self, dish, quantity=1, notes=None):
        """Додає нову страву до замовлення"""
        # Перевіряємо наявність страви
        if dish.is_available:
            # Перевіряємо чи страва вже є в замовленні
            item, created = OrderItem.objects.get_or_create(
                order=self,
                dish=dish,
                defaults={'quantity': quantity, 'notes': notes}
            )
            
            # Якщо страва вже була в замовленні, оновлюємо кількість
            if not created:
                item.quantity += quantity
                item.save()
                
            return item
        return None
    
    def remove_item(self, item_id):
        """Видаляє страву із замовлення"""
        try:
            item = self.items.get(id=item_id)
            item.delete()
            return True
        except OrderItem.DoesNotExist:
            return False
    
    def complete_order(self):
        """Завершує замовлення та звільняє стіл"""
        if self.is_paid:
            self.status = 'COMPLETED'
            self.save()
            
            # Звільняємо стіл
            self.table.status = 'FREE'
            self.table.save()
            
            # Віднімаємо інгредієнти зі складу
            for item in self.items.all():
                dish = item.dish
                for dish_ingredient in dish.dishingredient_set.all():
                    ingredient = dish_ingredient.ingredient
                    required_amount = dish_ingredient.amount * item.quantity
                    ingredient.decrease_stock(required_amount)
            
            return True
        return False
    
    def cancel_order(self):
        """Скасовує замовлення"""
        if self.status not in ['COMPLETED', 'CANCELED']:
            self.status = 'CANCELED'
            self.save()
            
            # Звільняємо стіл
            self.table.status = 'FREE'
            self.table.save()
            return True
        return False


class OrderItem(models.Model):
    """Модель для елементів замовлення (конкретні страви)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',
                             verbose_name=_('Замовлення'))
    dish = models.ForeignKey('menu.Dish', on_delete=models.PROTECT,
                           verbose_name=_('Страва'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Кількість'))
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                              verbose_name=_('Ціна'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    
    class Meta:
        verbose_name = _('Елемент замовлення')
        verbose_name_plural = _('Елементи замовлень')
    
    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"
    
    def save(self, *args, **kwargs):
        # Зберігаємо поточну ціну страви при створенні елемента замовлення
        if not self.price:
            self.price = self.dish.price
        super().save(*args, **kwargs)
    
    @property
    def total_price(self):
        """Загальна вартість за цей елемент замовлення"""
        return self.price * self.quantity