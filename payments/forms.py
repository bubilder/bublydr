from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Payment

class PaymentForm(forms.ModelForm):
    """Форма для створення і редагування платежу"""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
    
    def __init__(self, *args, **kwargs):
        # Видаляємо замовлення з kwargs, тому що воно не є полем форми
        self.order = kwargs.pop('order', None)
        
        super().__init__(*args, **kwargs)
        
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        payment = super().save(commit=False)
        
        # Якщо передали замовлення, зберігаємо його у платежі
        if self.order:
            payment.order = self.order
            
        if commit:
            payment.save()
        
        return payment

class PaymentFilterForm(forms.Form):
    """Форма для фільтрації платежів"""
    
    status = forms.ChoiceField(
        choices=[('', 'Всі статуси')] + list(Payment.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    payment_method = forms.ChoiceField(
        choices=[('', 'Всі способи оплати')] + list(Payment.PAYMENT_METHOD_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )