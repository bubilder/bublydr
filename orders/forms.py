from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    """Форма для створення і редагування замовлення"""
    
    class Meta:
        model = Order
        fields = ['table', 'customer_name', 'notes', 'discount_percent']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки вільні або зайняті столики (не зарезервовані або недоступні)
        from tables.models import Table
        self.fields['table'].queryset = Table.objects.filter(
            is_active=True, 
            status__in=['free', 'occupied']
        )

class OrderItemForm(forms.ModelForm):
    """Форма для додавання страви до замовлення"""
    
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки доступні страви
        from menu.models import Dish
        self.fields['dish'].queryset = Dish.objects.filter(is_available=True)
        
        # Додаткові атрибути для кількості
        self.fields['quantity'].widget.attrs.update({
            'min': '1',
            'max': '20',
            'class': 'form-control'
        })

class OrderStatusForm(forms.ModelForm):
    """Форма для зміни статусу замовлення"""
    
    class Meta:
        model = Order
        fields = ['status', 'payment_status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-select'