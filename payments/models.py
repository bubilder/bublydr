from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from accounts.models import User
from orders.models import Order

class Payment(models.Model):
    """Оплата замовлення в ресторані"""
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Готівка'),
        ('card', 'Банківська карта'),
        ('online', 'Онлайн-оплата'),
        ('transfer', 'Банківський переказ'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Очікування'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('refunded', 'Повернуто'),
    )
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.PROTECT, 
        related_name='payments',
        verbose_name=_('Замовлення')
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Сума')
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name=_('Спосіб оплати')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Час створення')
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_('Час завершення')
    )
    cashier = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        verbose_name=_('Касир')
    )
    transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_('Номер транзакції')
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('Примітки')
    )
    
    class Meta:
        verbose_name = _('Платіж')
        verbose_name_plural = _('Платежі')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платіж #{self.id} за замовлення #{self.order_id}"
    
    def complete(self):
        """Позначити платіж як завершений"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Оновлюємо статус замовлення
        self.order.payment_status = 'paid'
        self.order.save()
        
        return True
    
    def refund(self):
        """Повернути платіж"""
        self.status = 'refunded'
        self.save()
        
        # Оновлюємо статус замовлення
        self.order.payment_status = 'refunded'
        self.order.save()
        
        return True

class Receipt(models.Model):
    """Чек для оплати"""
    
    payment = models.OneToOneField(
        Payment, 
        on_delete=models.CASCADE,
        related_name='receipt',
        verbose_name=_('Платіж')
    )
    receipt_number = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_('Номер чека')
    )
    fiscal_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Фіскальний номер')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Час створення')
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Сума податку')
    )
    content = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_('Вміст чека')
    )
    is_printed = models.BooleanField(
        default=False, 
        verbose_name=_('Надрукований')
    )
    
    class Meta:
        verbose_name = _('Чек')
        verbose_name_plural = _('Чеки')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Чек #{self.receipt_number} (Платіж #{self.payment_id})"
    
    def generate_content(self):
        """Генерує зміст чека на основі платежу та замовлення"""
        order = self.payment.order
        order_items = order.items.all()
        
        content = f"Чек #{self.receipt_number}\n"
        content += f"Дата: {self.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        content += "-" * 40 + "\n"
        content += "Найменування     Кіл-сть  Ціна    Сума\n"
        content += "-" * 40 + "\n"
        
        for item in order_items:
            name = item.dish.name[:15].ljust(15)
            qty = str(item.quantity).ljust(8)
            price = f"{item.price:.2f}".ljust(8)
            total = f"{item.subtotal:.2f}"
            content += f"{name} {qty} {price} {total}\n"
        
        content += "-" * 40 + "\n"
        content += f"Всього: {order.total_price:.2f}\n"
        
        if order.discount_percent > 0:
            discount = order.total_price * (order.discount_percent / Decimal('100'))
            content += f"Знижка ({order.discount_percent}%): {discount:.2f}\n"
            content += f"До оплати: {order.total_price - discount:.2f}\n"
        
        content += "-" * 40 + "\n"
        content += f"Спосіб оплати: {self.payment.get_payment_method_display()}\n"
        content += f"Касир: {self.payment.cashier.get_full_name() if self.payment.cashier else 'Система'}\n"
        content += "-" * 40 + "\n"
        content += "Дякуємо за покупку!\n"
        
        self.content = content
        self.save()
        
        return content
    
    def mark_as_printed(self):
        """Позначити чек як надрукований"""
        self.is_printed = True
        self.save()