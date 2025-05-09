from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderItem
from menu.models import Dish, Category
from tables.models import Table
from payments.models import Payment
from inventory.models import Ingredient

@login_required
def dashboard_home_view(request):
    """Головна сторінка з основним оглядом"""
    
    # Отримуємо статистику за сьогодні
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    
    # Статистика замовлень
    today_orders = Order.objects.filter(created_at__range=(today_start, today_end))
    today_order_count = today_orders.count()
    today_sales = sum(order.total_price for order in today_orders.filter(is_paid=True))
    
    # Статистика столів
    tables = Table.objects.all()
    free_tables = tables.filter(status='FREE').count()
    occupied_tables = tables.filter(status='OCCUPIED').count()
    reserved_tables = tables.filter(status='RESERVED').count()
    
    # Активні замовлення
    active_orders = Order.objects.filter(status__in=['PENDING', 'IN_PROGRESS', 'READY'])
    
    # Інгредієнти з малим запасом
    low_stock_ingredients = Ingredient.objects.filter(current_stock__lte=F('minimum_stock'))
    
    context = {
        'today_order_count': today_order_count,
        'today_sales': today_sales,
        'free_tables': free_tables,
        'occupied_tables': occupied_tables,
        'reserved_tables': reserved_tables,
        'active_orders': active_orders,
        'low_stock_ingredients': low_stock_ingredients,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def stats_view(request):
    """Детальна статистика продажів"""
    
    # Отримуємо період для статистики
    period = request.GET.get('period', 'week')
    
    today = timezone.now().date()
    if period == 'day':
        start_date = today
        date_label = "Сьогодні"
    elif period == 'week':
        start_date = today - timedelta(days=7)
        date_label = "За тиждень"
    elif period == 'month':
        start_date = today - timedelta(days=30)
        date_label = "За місяць"
    else:  # 'year'
        start_date = today - timedelta(days=365)
        date_label = "За рік"
    
    start_datetime = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
    
    # Замовлення за вказаний період
    orders = Order.objects.filter(created_at__gte=start_datetime, is_paid=True)
    
    # Загальна сума продажів
    total_sales = sum(order.total_price for order in orders)
    
    # Кількість замовлень
    order_count = orders.count()
    
    # Середній чек
    average_check = total_sales / order_count if order_count > 0 else 0
    
    # Найпопулярніші страви
    popular_dishes = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'dish__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:10]
    
    # Продажі за категоріями
    category_sales = OrderItem.objects.filter(
        order__in=orders
    ).values(
        'dish__category__name'
    ).annotate(
        total_sales=Sum(F('price') * F('quantity'))
    ).order_by('-total_sales')
    
    # Продажі за способом оплати
    payment_methods = Payment.objects.filter(
        order__in=orders
    ).values(
        'payment_method'
    ).annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    context = {
        'period': period,
        'date_label': date_label,
        'total_sales': total_sales,
        'order_count': order_count,
        'average_check': average_check,
        'popular_dishes': popular_dishes,
        'category_sales': category_sales,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'dashboard/stats.html', context)