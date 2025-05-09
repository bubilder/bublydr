from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Table, Reservation

class TableForm(forms.ModelForm):
    """Форма для створення та редагування столів"""
    class Meta:
        model = Table
        fields = ['number', 'capacity', 'status', 'location', 'notes']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReservationForm(forms.ModelForm):
    """Форма для створення та редагування резервацій"""
    reservation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=_('Дата резервації')
    )
    reservation_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label=_('Час резервації')
    )
    
    class Meta:
        model = Reservation
        fields = ['table', 'customer_name', 'customer_phone', 'number_of_guests', 
                  'reservation_date', 'reservation_time', 'notes']
        widgets = {
            'table': forms.Select(attrs={'class': 'form-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        """Перевіряємо чи кількість гостей не перевищує місткість столу"""
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        number_of_guests = cleaned_data.get('number_of_guests')
        
        if table and number_of_guests and number_of_guests > table.capacity:
            raise forms.ValidationError(
                _("Кількість гостей перевищує місткість столу (%(capacity)s)"),
                code='invalid_guests',
                params={'capacity': table.capacity}
            )
        
        return cleaned_data