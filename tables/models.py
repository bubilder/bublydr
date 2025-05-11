from django.db import models
from django.utils.translation import gettext_lazy as _

class Table(models.Model):
    """Модель столика у ресторані"""
    
    STATUS_CHOICES = (
        ('free', 'Вільний'),
        ('occupied', 'Зайнятий'),
        ('reserved', 'Зарезервований'),
        ('unavailable', 'Недоступний'),
    )
    
    number = models.IntegerField(verbose_name=_('Номер столика'), unique=True)
    capacity = models.IntegerField(verbose_name=_('Кількість місць'))
    location = models.CharField(max_length=100, verbose_name=_('Розташування'), 
                               help_text=_('Наприклад: Біля вікна, На терасі'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='free', verbose_name=_('Статус'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    
    class Meta:
        verbose_name = _('Столик')
        verbose_name_plural = _('Столики')
        ordering = ['number']
    
    def __str__(self):
        return f"Столик №{self.number} ({self.get_status_display()})"
    
    @property
    def is_available(self):
        """Перевіряє, чи доступний столик для бронювання"""
        return self.status in ['free'] and self.is_active

class Reservation(models.Model):
    """Бронювання столика"""
    
    STATUS_CHOICES = (
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
        ('completed', 'Завершено'),
    )
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, 
                             related_name='reservations', verbose_name=_('Столик'))
    customer_name = models.CharField(max_length=100, verbose_name=_("Ім'я клієнта"))
    customer_phone = models.CharField(max_length=20, verbose_name=_('Телефон клієнта'))
    customer_email = models.EmailField(blank=True, null=True, verbose_name=_('Email клієнта'))
    reservation_date = models.DateField(verbose_name=_('Дата бронювання'))
    reservation_time = models.TimeField(verbose_name=_('Час бронювання'))
    duration = models.IntegerField(default=120, verbose_name=_('Тривалість (хвилин)'))
    guests_count = models.IntegerField(verbose_name=_('Кількість гостей'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='pending', verbose_name=_('Статус'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примітки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    
    class Meta:
        verbose_name = _('Бронювання')
        verbose_name_plural = _('Бронювання')
        ordering = ['-reservation_date', '-reservation_time']
    
    def __str__(self):
        return f"Бронювання {self.table} на {self.reservation_date} {self.reservation_time}"