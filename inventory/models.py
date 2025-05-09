from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal

class Ingredient(models.Model):
    """Модель для інгредієнтів, які використовуються у стравах"""
    name = models.CharField(max_length=100, verbose_name=_('Назва'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Опис'))
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name=_('Поточна кількість'))
    unit = models.CharField(max_length=20, verbose_name=_('Одиниця виміру'))
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                     verbose_name=_('Мінімальна кількість'))
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2,
                                      verbose_name=_('Ціна за одиницю'))
    
    class Meta:
        verbose_name = _('Інгредієнт')
        verbose_name_plural = _('Інгредієнти')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"
    
    @property
    def is_low_stock(self):
        """Чи закінчується інгредієнт"""
        return self.current_stock <= self.minimum_stock
    
    @property
    def total_value(self):
        """Загальна вартість наявного інгредієнту"""
        return self.current_stock * self.price_per_unit
    
    def decrease_stock(self, amount):
        """Зменшує запас інгредієнту"""
        if amount > 0:
            self.current_stock = max(0, self.current_stock - amount)
            self.save()
            
            # Записуємо транзакцію
            transaction = StockTransaction(
                ingredient=self,
                transaction_type='DECREASE',
                amount=amount,
                unit_price=self.price_per_unit
            )
            transaction.save()
    
    def increase_stock(self, amount, price_per_unit=None):
        """Збільшує запас інгредієнту"""
        if amount > 0:
            # Оновлюємо ціну, якщо вона вказана
            if price_per_unit:
                # Середньозважена ціна
                total_value = (self.current_stock * self.price_per_unit) + (amount * price_per_unit)
                new_total_quantity = self.current_stock + amount
                new_price_per_unit = total_value / new_total_quantity if new_total_quantity > 0 else price_per_unit
                
                self.price_per_unit = new_price_per_unit
            
            self.current_stock += amount
            self.save()
            
            # Записуємо транзакцію
            transaction = StockTransaction(
                ingredient=self,
                transaction_type='INCREASE',
                amount=amount,
                unit_price=price_per_unit or self.price_per_unit
            )
            transaction.save()

class StockTransaction(models.Model):
    """Модель для відстеження транзакцій інгредієнтів"""
    
    TRANSACTION_TYPES = (
        ('INCREASE', 'Поповнення'),
        ('DECREASE', 'Витрата'),
    )
    
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='transactions',
                                 verbose_name=_('Інгредієнт'))
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES,
                                     verbose_name=_('Тип транзакції'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Кількість'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Ціна за одиницю'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 blank=True, null=True, verbose_name=_('Створив'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    
    class Meta:
        verbose_name = _('Транзакція запасу')
        verbose_name_plural = _('Транзакції запасів')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.ingredient.name}: {self.amount} {self.ingredient.unit}"
    
    @property
    def total_price(self):
        """Загальна вартість транзакції"""
        return self.amount * self.unit_price