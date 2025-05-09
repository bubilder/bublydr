from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Category, Dish
from .forms import CategoryForm, DishForm, DishIngredientFormSet

def is_admin(user):
    """Перевірка чи користувач є адміністратором"""
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@login_required
def menu_list_view(request):
    """Перегляд меню для офіціантів"""
    categories = Category.objects.filter(is_active=True)
    search_query = request.GET.get('search', '')
    
    if search_query:
        dishes = Dish.objects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query),
            is_available=True
        )
        return render(request, 'menu/menu_search.html', {
            'dishes': dishes,
            'search_query': search_query
        })
    
    return render(request, 'menu/menu_list.html', {'categories': categories})

@login_required
def dish_detail_view(request, pk):
    """Детальна інформація про страву"""
    dish = get_object_or_404(Dish, pk=pk)
    return render(request, 'menu/dish_detail.html', {'dish': dish})

@user_passes_test(is_admin)
def menu_management_view(request):
    """Управління меню (для адміністраторів)"""
    categories = Category.objects.all()
    return render(request, 'menu/menu_management.html', {'categories': categories})

@user_passes_test(is_admin)
def category_create_view(request):
    """Створення нової категорії"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Категорію успішно створено"))
            return redirect('menu:manage')
    else:
        form = CategoryForm()
    
    return render(request, 'menu/category_form.html', {'form': form})

@user_passes_test(is_admin)
def category_update_view(request, pk):
    """Редагування категорії"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Категорію успішно оновлено"))
            return redirect('menu:manage')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'menu/category_form.html', {'form': form, 'category': category})

@user_passes_test(is_admin)
def category_delete_view(request, pk):
    """Видалення категорії"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, _("Категорію успішно видалено"))
        return redirect('menu:manage')
    
    return render(request, 'menu/category_confirm_delete.html', {'category': category})

@user_passes_test(is_admin)
def dish_create_view(request):
    """Створення нової страви"""
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            dish = form.save()
            
            # Обробка інгредієнтів
            formset = DishIngredientFormSet(request.POST, instance=dish)
            if formset.is_valid():
                formset.save()
                dish.check_availability()  # Перевірка наявності інгредієнтів
                messages.success(request, _("Страву успішно створено"))
                return redirect('menu:manage')
            else:
                dish.delete()  # Якщо інгредієнти неправильні, видаляємо страву
        else:
            formset = DishIngredientFormSet(instance=Dish())
    else:
        form = DishForm()
        formset = DishIngredientFormSet(instance=Dish())
    
    return render(request, 'menu/dish_form.html', {
        'form': form,
        'formset': formset
    })

@user_passes_test(is_admin)
def dish_update_view(request, pk):
    """Редагування страви"""
    dish = get_object_or_404(Dish, pk=pk)
    
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            dish = form.save()
            
            formset = DishIngredientFormSet(request.POST, instance=dish)
            if formset.is_valid():
                formset.save()
                dish.check_availability()  # Перевірка наявності інгредієнтів
                messages.success(request, _("Страву успішно оновлено"))
                return redirect('menu:manage')
    else:
        form = DishForm(instance=dish)
        formset = DishIngredientFormSet(instance=dish)
    
    return render(request, 'menu/dish_form.html', {
        'form': form,
        'formset': formset,
        'dish': dish
    })

@user_passes_test(is_admin)
def dish_delete_view(request, pk):
    """Видалення страви"""
    dish = get_object_or_404(Dish, pk=pk)
    
    if request.method == 'POST':
        dish.delete()
        messages.success(request, _("Страву успішно видалено"))
        return redirect('menu:manage')
    
    return render(request, 'menu/dish_confirm_delete.html', {'dish': dish})