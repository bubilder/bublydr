from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from accounts.models import User
from menu.models import Dish
from tables.models import Table

class Order(models.Model):
    """Замовлення в ресторані"""
    
    STATUS_CHOICES = (
        ('new', 'Нове'),
        ('processing', 'В обробці'),
        ('ready', 'Готове'),
        ('delivered', 'Доставлене'),
        ('completed', 'Завершене'),
        ('cancelled', 'Скасоване'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Очікує оплати'),
        ('paid', 'Оплачено'),
        ('refunded', 'Повернуто'),
    )
    
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='orders', verbose_name=_('Столик'))
    waiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='orders', verbose_name=_('Офіціант'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new',
                             verbose_name=_('Статус'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, 
                                     default='pending', verbose_name=_('Статус оплати'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Час створення'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Час оновлення'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Час завершення'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    customer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Ім'я клієнта"))
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                         verbose_name=_('Знижка (%)'))
    
    class Meta:
        verbose_name = _('Замовлення')
        verbose_name_plural = _('Замовлення')
        ordering = ['-created_at']
    
    def __str__(self):
        if self.table:
            return f"Замовлення #{self.id} (Столик №{self.table.number})"
        else:
            return f"Замовлення #{self.id}"
    
    @property
    def total_price(self):
        """Загальна вартість замовлення з урахуванням кількості та знижки"""
        total = sum(item.subtotal for item in self.items.all())
        if self.discount_percent:
            discount = total * (self.discount_percent / Decimal('100'))
            return total - discount
        return total
    
    @property
    def items_count(self):
        """Загальна кількість страв у замовленні"""
        return sum(item.quantity for item in self.items.all())
    
    def mark_as_completed(self):
        """Позначити замовлення як завершене"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_paid(self):
        """Позначити замовлення як оплачене"""
        self.payment_status = 'paid'
        self.save()

class OrderItem(models.Model):
    """Окрема страва в замовленні"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',
                             verbose_name=_('Замовлення'))
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name='+',
                            verbose_name=_('Страва'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Кількість'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Ціна за одиницю'))
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='new',
                             verbose_name=_('Статус'))
    notes = models.CharField(max_length=255, blank=True, null=True, 
                            verbose_name=_('Особливі побажання'))
    
    class Meta:
        verbose_name = _('Елемент замовлення')
        verbose_name_plural = _('Елементи замовлення')
    
    def __str__(self):
        return f"{self.dish.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        """Вартість цієї позиції з урахуванням кількості"""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        # При першому збереженні, зберігаємо поточну ціну страви
        if not self.price:
            self.price = self.dish.price
        super().save(*args, **kwargs)