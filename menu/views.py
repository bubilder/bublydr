from django.shortcuts import render, get_object_or_404
from .models import Category, Dish

def menu_list(request):
    """Відображає список всіх категорій у меню"""
    categories = Category.objects.filter(is_active=True)
    return render(request, 'menu/list.html', {
        'categories': categories
    })

def category_detail(request, category_id):
    """Відображає одну категорію та всі її страви"""
    category = get_object_or_404(Category, id=category_id, is_active=True)
    dishes = category.dishes.filter(is_available=True)
    return render(request, 'menu/category_detail.html', {
        'category': category,
        'dishes': dishes
    })

def dish_detail(request, dish_id):
    """Відображає деталі конкретної страви"""
    dish = get_object_or_404(Dish, id=dish_id, is_available=True)
    return render(request, 'menu/dish_detail.html', {
        'dish': dish
    })