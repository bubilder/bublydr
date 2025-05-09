from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Payment(models.Model):
    """Модель для оплат замовлень"""
    
    PAYMENT_METHODS = (
        ('CASH', 'Готівка'),
        ('CARD', 'Картка'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField('orders.Order', on_delete=models.PROTECT, related_name='payment',
                               verbose_name=_('Замовлення'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Сума'))
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS,
                                   verbose_name=_('Спосіб оплати'))
    amount_tendered = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                       verbose_name=_('Отримана сума'))
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                     verbose_name=_('Сума решти'))
    transaction_id = models.CharField(max_length=100, blank=True, null=True,
                                    verbose_name=_('ID транзакції'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    
    class Meta:
        verbose_name = _('Платіж')
        verbose_name_plural = _('Платежі')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Платіж {self.id} - {self.order}"
    
    def save(self, *args, **kwargs):
        # Автоматичне обчислення суми решти для готівкових платежів
        if self.payment_method == 'CASH' and self.amount_tendered:
            self.change_amount = self.amount_tendered - self.amount
        super().save(*args, **kwargs)