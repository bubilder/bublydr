from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    """Форма для створення та редагування замовлення"""
    class Meta:
        model = Order
        fields = ['table', 'status', 'notes', 'discount']
        widgets = {
            'table': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class OrderItemForm(forms.ModelForm):
    """Форма для додавання страви до замовлення"""
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'notes']
        widgets = {
            'dish': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class OrderPaymentForm(forms.Form):
    """Форма для оплати замовлення"""
    PAYMENT_CHOICES = (
        ('CASH', 'Готівка'),
        ('CARD', 'Картка'),
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('Спосіб оплати')
    )
    
    amount_tendered = forms.DecimalField(
        required=False,  # Необов'язкове для оплати карткою
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label=_('Отримано грошей')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        amount_tendered = cleaned_data.get('amount_tendered')
        
        # Для готівкової оплати необхідно вказати отриману суму
        if payment_method == 'CASH' and not amount_tendered:
            self.add_error('amount_tendered', _('Для готівкової оплати необхідно вказати отриману суму'))
            
        return cleaned_data