from django import forms
from django.forms import inlineformset_factory
from .models import Category, Dish, DishIngredient

class CategoryForm(forms.ModelForm):
    """Форма для створення та редагування категорій"""
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DishForm(forms.ModelForm):
    """Форма для створення та редагування страв"""
    class Meta:
        model = Dish
        fields = ['name', 'description', 'price', 'category', 'image', 
                  'is_available', 'preparation_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DishIngredientForm(forms.ModelForm):
    """Форма для інгредієнтів страви"""
    class Meta:
        model = DishIngredient
        fields = ['ingredient', 'amount', 'unit']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Створюємо formset для інгредієнтів
DishIngredientFormSet = inlineformset_factory(
    Dish, 
    DishIngredient, 
    form=DishIngredientForm,
    extra=1,
    can_delete=True
)