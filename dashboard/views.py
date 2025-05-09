from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum

from .models import Ingredient, StockTransaction
from .forms import IngredientForm, StockTransactionForm

def is_admin(user):
    """Перевірка чи користувач є адміністратором"""
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def inventory_list_view(request):
    """Відображає список всіх інгредієнтів"""
    ingredients = Ingredient.objects.all().order_by('name')
    
    # Обчислення загальної вартості запасів
    total_inventory_value = sum(ingredient.total_value for ingredient in ingredients)
    
    # Знаходження інгредієнтів з малим запасом
    low_stock_ingredients = [ingredient for ingredient in ingredients if ingredient.is_low_stock]
    
    context = {
        'ingredients': ingredients,
        'total_inventory_value': total_inventory_value,
        'low_stock_ingredients': low_stock_ingredients
    }
    
    return render(request, 'inventory/inventory_list.html', context)

@login_required
@user_passes_test(is_admin)
def ingredient_create_view(request):
    """Створення нового інгредієнта"""
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            
            # Додавання початкової транзакції, якщо є запас
            if ingredient.current_stock > 0:
                StockTransaction.objects.create(
                    ingredient=ingredient,
                    transaction_type='INCREASE',
                    amount=ingredient.current_stock,
                    unit_price=ingredient.price_per_unit,
                    created_by=request.user,
                    notes=_("Початковий запас")
                )
            
            messages.success(request, _("Інгредієнт успішно створено"))
            return redirect('inventory:list')
    else:
        form = IngredientForm()
    
    return render(request, 'inventory/ingredient_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def ingredient_update_view(request, pk):
    """Редагування інгредієнта"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    old_stock = ingredient.current_stock
    
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            new_ingredient = form.save()
            
            # Якщо кількість змінилась, створюємо транзакцію
            new_stock = new_ingredient.current_stock
            if new_stock != old_stock:
                if new_stock > old_stock:
                    # Збільшення запасу
                    StockTransaction.objects.create(
                        ingredient=new_ingredient,
                        transaction_type='INCREASE',
                        amount=new_stock - old_stock,
                        unit_price=new_ingredient.price_per_unit,
                        created_by=request.user,
                        notes=_("Коригування запасу")
                    )
                else:
                    # Зменшення запасу
                    StockTransaction.objects.create(
                        ingredient=new_ingredient,
                        transaction_type='DECREASE',
                        amount=old_stock - new_stock,
                        unit_price=new_ingredient.price_per_unit,
                        created_by=request.user,
                        notes=_("Коригування запасу")
                    )
            
            messages.success(request, _("Інгредієнт успішно оновлено"))
            return redirect('inventory:list')
    else:
        form = IngredientForm(instance=ingredient)
    
    return render(request, 'inventory/ingredient_form.html', {
        'form': form,
        'ingredient': ingredient
    })

@login_required
@user_passes_test(is_admin)
def ingredient_delete_view(request, pk):
    """Видалення інгредієнта"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    
    # Перевіряємо, чи інгредієнт використовується у стравах
    dishes_count = ingredient.dishes.count()
    
    if request.method == 'POST':
        if dishes_count > 0 and not request.POST.get('confirm_delete'):
            messages.error(request, _("Цей інгредієнт використовується в стравах. Перегляньте прикріплені страви перед видаленням."))
            return redirect('inventory:ingredient_detail', pk=pk)
        
        ingredient.delete()
        messages.success(request, _("Інгредієнт успішно видалено"))
        return redirect('inventory:list')
    
    return render(request, 'inventory/ingredient_confirm_delete.html', {
        'ingredient': ingredient,
        'dishes_count': dishes_count
    })

@login_required
@user_passes_test(is_admin)
def ingredient_detail_view(request, pk):
    """Детальна інформація про інгредієнт та його транзакції"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    transactions = ingredient.transactions.all().order_by('-created_at')
    
    # Отримуємо страви, які використовують цей інгредієнт
    dishes = ingredient.dishes.all()
    
    context = {
        'ingredient': ingredient,
        'transactions': transactions,
        'dishes': dishes
    }
    
    return render(request, 'inventory/ingredient_detail.html', context)

@login_required
@user_passes_test(is_admin)
def add_stock_view(request, pk):
    """Додавання запасу інгредієнта"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            unit_price = form.cleaned_data.get('unit_price') or ingredient.price_per_unit
            notes = form.cleaned_data.get('notes')
            
            # Збільшення запасу
            ingredient.increase_stock(amount, unit_price)
            
            # Створення запису транзакції
            transaction = StockTransaction(
                ingredient=ingredient,
                transaction_type='INCREASE',
                amount=amount,
                unit_price=unit_price,
                created_by=request.user,
                notes=notes
            )
            transaction.save()
            
            messages.success(request, _("Запас успішно додано"))
            return redirect('inventory:ingredient_detail', pk=pk)
    else:
        form = StockTransactionForm(initial={'unit_price': ingredient.price_per_unit})
    
    return render(request, 'inventory/add_stock.html', {
        'form': form,
        'ingredient': ingredient
    })

@login_required
@user_passes_test(is_admin)
def remove_stock_view(request, pk):
    """Видалення запасу інгредієнта"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            notes = form.cleaned_data.get('notes')
            
            # Перевіряємо, чи є достатня кількість
            if ingredient.current_stock < amount:
                messages.error(request, _("Недостатня кількість для видалення"))
                return redirect('inventory:ingredient_detail', pk=pk)
            
            # Зменшення запасу
            ingredient.decrease_stock(amount)
            
            # Створення запису транзакції
            transaction = StockTransaction(
                ingredient=ingredient,
                transaction_type='DECREASE',
                amount=amount,
                unit_price=ingredient.price_per_unit,
                created_by=request.user,
                notes=notes
            )
            transaction.save()
            
            messages.success(request, _("Запас успішно видалено"))
            return redirect('inventory:ingredient_detail', pk=pk)
    else:
        form = StockTransactionForm()
    
    return render(request, 'inventory/remove_stock.html', {
        'form': form,
        'ingredient': ingredient
    })

@login_required
@user_passes_test(is_admin)
def stock_transaction_list_view(request):
    """Відображення списку всіх транзакцій запасу"""
    transactions = StockTransaction.objects.all().order_by('-created_at')
    
    context = {
        'transactions': transactions
    }
    
    return render(request, 'inventory/transaction_list.html', context)