from django import forms
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from .models import (
    Product, ProductCategory, Unit, Supplier, Purchase, PurchaseItem,
    Consumption, Recipe, RecipeIngredient
)

class ProductForm(forms.ModelForm):
    """Форма для створення і редагування продукту"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'unit', 'price_per_unit', 
            'current_quantity', 'minimum_quantity', 'description', 
            'barcode', 'is_active'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ProductCategoryForm(forms.ModelForm):
    """Форма для створення і редагування категорії продуктів"""
    
    class Meta:
        model = ProductCategory
        fields = ['name', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UnitForm(forms.ModelForm):
    """Форма для створення і редагування одиниць виміру"""
    
    class Meta:
        model = Unit
        fields = ['name', 'short_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class SupplierForm(forms.ModelForm):
    """Форма для створення і редагування постачальників"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'phone', 'email', 
            'address', 'notes', 'is_active'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class PurchaseForm(forms.ModelForm):
    """Форма для створення і редагування закупівель"""
    
    expected_delivery = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Очікувана дата доставки')
    )
    
    class Meta:
        model = Purchase
        fields = [
            'supplier', 'expected_delivery', 'notes'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки активних постачальників
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)

class PurchaseItemForm(forms.ModelForm):
    """Форма для додавання продукту до закупівлі"""
    
    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'price_per_unit']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки активні продукти
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Додаткові атрибути для кількості та ціни
        for field_name in ['quantity', 'price_per_unit']:
            self.fields[field_name].widget.attrs.update({
                'min': '0.01',
                'step': '0.01'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        price_per_unit = cleaned_data.get('price_per_unit')
        
        # Якщо ціна не вказана, використовуємо поточну ціну продукту
        if product and not price_per_unit:
            cleaned_data['price_per_unit'] = product.price_per_unit
        
        return cleaned_data

class ConsumptionForm(forms.ModelForm):
    """Форма для створення списання продуктів"""
    
    class Meta:
        model = Consumption
        fields = ['product', 'quantity', 'reason', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Для поля reason використовуємо form-select
        self.fields['reason'].widget.attrs['class'] = 'form-select'
        
        # Показуємо тільки активні продукти з позитивною кількістю
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            current_quantity__gt=0
        )
        
        # Додаткові атрибути для кількості
        self.fields['quantity'].widget.attrs.update({
            'min': '0.01',
            'step': '0.01'
        })
    
    def clean_quantity(self):
        product = self.cleaned_data.get('product')
        quantity = self.cleaned_data.get('quantity')
        
        # Перевіряємо, чи не перевищує кількість списання поточну кількість продукту
        if product and quantity:
            if quantity > product.current_quantity:
                raise forms.ValidationError(
                    _('Неможливо списати %(quantity)s %(unit)s продукту %(product)s, '
                      'оскільки доступно лише %(available)s %(unit)s.'),
                    params={
                        'quantity': quantity,
                        'unit': product.unit.short_name,
                        'product': product.name,
                        'available': product.current_quantity
                    }
                )
        
        return quantity

class RecipeForm(forms.ModelForm):
    """Форма для створення і редагування рецепту"""
    
    class Meta:
        model = Recipe
        fields = ['dish', 'description', 'is_active']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки ті страви, для яких ще немає рецепту
        from menu.models import Dish
        existing_recipes = Recipe.objects.values_list('dish_id', flat=True)
        
        if self.instance.pk:  # Якщо це редагування існуючого рецепту
            self.fields['dish'].queryset = Dish.objects.filter(
                is_available=True,
                id=self.instance.dish_id
            )
            # Робимо поле "dish" неактивним, оскільки не можна змінювати страву для існуючого рецепту
            self.fields['dish'].widget.attrs['disabled'] = 'disabled'
        else:  # Якщо це створення нового рецепту
            self.fields['dish'].queryset = Dish.objects.filter(
                is_available=True
            ).exclude(id__in=existing_recipes)

class RecipeIngredientForm(forms.ModelForm):
    """Форма для додавання інгредієнта до рецепту"""
    
    class Meta:
        model = RecipeIngredient
        fields = ['product', 'quantity', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо класи Bootstrap до полів форми
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Показуємо тільки активні продукти
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Додаткові атрибути для кількості
        self.fields['quantity'].widget.attrs.update({
            'min': '0.01',
            'step': '0.01'
        })

class ProductFilterForm(forms.Form):
    """Форма для фільтрації продуктів"""
    
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        required=False,
        empty_label="Всі категорії",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    low_stock_only = forms.BooleanField(
        required=False,
        label=_('Тільки з низьким запасом'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    search = forms.CharField(
        required=False,
        label=_('Пошук'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва продукту'})
    )