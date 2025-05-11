from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Table, Reservation

class TableForm(forms.ModelForm):
    """Форма для створення і редагування столика"""
    
    class Meta:
        model = Table
        fields = ['number', 'capacity', 'location', 'status', 'notes', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ReservationForm(forms.ModelForm):
    """Форма для створення і редагування бронювання"""
    
    reservation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Дата бронювання')
    )
    reservation_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label=_('Час бронювання')
    )
    
    class Meta:
        model = Reservation
        fields = ['table', 'customer_name', 'customer_phone', 'customer_email', 
                 'reservation_date', 'reservation_time', 'duration', 'guests_count', 
                 'status', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки активні столики
        self.fields['table'].queryset = Table.objects.filter(is_active=True)