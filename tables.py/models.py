from django.db import models
from django.utils.translation import gettext_lazy as _

class Table(models.Model):
    """Модель столу в ресторані"""
    
    STATUS_CHOICES = (
        ('FREE', 'Вільний'),
        ('OCCUPIED', 'Зайнятий'),
        ('RESERVED', 'Зарезервований'),
    )
    
    number = models.PositiveIntegerField(unique=True, verbose_name=_('Номер столу'))
    capacity = models.PositiveIntegerField(verbose_name=_('Кількість місць'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='FREE', verbose_name=_('Статус'))
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Розташування'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    
    class Meta:
        verbose_name = _('Стіл')
        verbose_name_plural = _('Столи')
        ordering = ['number']
    
    def __str__(self):
        return f"Стіл №{self.number} ({self.get_status_display()})"
    
    @property
    def is_free(self):
        """Перевірка чи стіл вільний"""
        return self.status == 'FREE'
    
    @property
    def current_order(self):
        """Повертає поточне замовлення для столу, якщо таке є"""
        active_order = self.orders.filter(status__in=['PENDING', 'IN_PROGRESS']).first()
        return active_order
    
    def set_status(self, status):
        """Оновлює статус столу"""
        self.status = status
        self.save()

class Reservation(models.Model):
    """Модель для резервації столика"""
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations',
                              verbose_name=_('Стіл'))
    customer_name = models.CharField(max_length=100, verbose_name=_('Ім\'я клієнта'))
    customer_phone = models.CharField(max_length=15, verbose_name=_('Телефон клієнта'))
    number_of_guests = models.PositiveIntegerField(default=1, verbose_name=_('Кількість гостей'))
    reservation_date = models.DateField(verbose_name=_('Дата резервації'))
    reservation_time = models.TimeField(verbose_name=_('Час резервації'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    
    class Meta:
        verbose_name = _('Резервація')
        verbose_name_plural = _('Резервації')
        ordering = ['reservation_date', 'reservation_time']
    
    def __str__(self):
        return f"Резервація: {self.customer_name}, стіл №{self.table.number}, {self.reservation_date}"
    
    def save(self, *args, **kwargs):
        """При збереженні резервації оновлюємо статус столу"""
        super().save(*args, **kwargs)
        self.table.set_status('RESERVED')