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
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Якщо форма вже відправлена і страва вибрана
        if self.is_bound and 'dish' in self.data:
            try:
                dish_id = int(self.data.get('dish'))
                dish = Dish.objects.get(id=dish_id)
                
                # Встановлюємо максимальну кількість
                max_available = dish.available_quantity()
                self.fields['quantity'].widget.attrs['max'] = max_available
                self.fields['quantity'].widget.attrs['data-max'] = max_available
                
                # Додаємо повідомлення про максимальну кількість
                if max_available <= 0:
                    self.fields['quantity'].help_text = f"Неможливо приготувати цю страву! Недостатньо інгредієнтів."
                else:
                    self.fields['quantity'].help_text = f"Максимально доступно: {max_available}"
            except:
                pass

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