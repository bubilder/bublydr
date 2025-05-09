from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Ingredient, StockTransaction

class IngredientForm(forms.ModelForm):
    """Форма для створення та редагування інгредієнтів"""
    class Meta:
        model = Ingredient
        fields = ['name', 'description', 'current_stock', 'unit', 
                  'minimum_stock', 'price_per_unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class StockTransactionForm(forms.Form):
    """Форма для додавання або видалення запасу інгредієнта"""
    amount = forms.DecimalField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label=_('Кількість')
    )
    unit_price = forms.DecimalField(
        min_value=0.01,
        required=False,  # Необов'язкове для видалення запасу
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label=_('Ціна за одиницю')
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label=_('Примітки')
    )