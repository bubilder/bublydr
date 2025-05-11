from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
import datetime

# Імпортуємо моделі даних з інших додатків
from menu.models import Dish, Category
from orders.models import Order, OrderItem
from tables.models import Table, Reservation
from payments.models import Payment
from inventory.models import Product
from django.db.models import Sum, Count, Avg, F

@login_required
def dashboard_home(request):
    """Головна сторінка панелі керування ресторану"""
    
    # Отримуємо поточну дату та попередній день
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    last_7_days = today - datetime.timedelta(days=7)
    last_30_days = today - datetime.timedelta(days=30)
    
    # Статистика замовлень
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_yesterday = Order.objects.filter(created_at__date=yesterday).count()
    orders_last_7_days = Order.objects.filter(created_at__date__gte=last_7_days).count()
    
    # Статистика доходів
    completed_payments = Payment.objects.filter(status='completed')
    total_revenue = completed_payments.aggregate(total=Sum('amount'))['total'] or 0
    revenue_today = completed_payments.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0
    revenue_yesterday = completed_payments.filter(created_at__date=yesterday).aggregate(total=Sum('amount'))['total'] or 0
    revenue_last_7_days = completed_payments.filter(created_at__date__gte=last_7_days).aggregate(total=Sum('amount'))['total'] or 0
    
    # Статистика столиків
    total_tables = Table.objects.filter(is_active=True).count()
    occupied_tables = Table.objects.filter(status='occupied').count()
    free_tables = Table.objects.filter(status='free').count()
    reserved_tables = Table.objects.filter(status='reserved').count()
    
    # Популярні страви (топ-5)
    popular_dishes = OrderItem.objects.values('dish__name').annotate(
        total_ordered=Count('id')
    ).order_by('-total_ordered')[:5]
    
    # Активні замовлення (які ще не завершені)
    active_orders = Order.objects.filter(
        status__in=['new', 'processing', 'ready', 'delivered'],
        payment_status='pending',
    ).order_by('-created_at')[:10]
    
    # Найближчі бронювання
    upcoming_reservations = Reservation.objects.filter(
        reservation_date__gte=today,
        status='confirmed'
    ).order_by('reservation_date', 'reservation_time')[:10]
    
    # Продукти з низьким запасом
    try:
        low_stock_products = Product.objects.filter(
            is_active=True,
            current_quantity__lt=F('minimum_quantity')
        )[:10]
    except:
        low_stock_products = []
    
    # Статистика броні столиків
    reservations_today = Reservation.objects.filter(reservation_date=today).count()
    reservations_tomorrow = Reservation.objects.filter(reservation_date=today + datetime.timedelta(days=1)).count()
    
    return render(request, 'dashboard/home.html', {
        # Загальна інформація
        'today': today,
        'yesterday': yesterday,
        
        # Статистика замовлень
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_yesterday': orders_yesterday,
        'orders_last_7_days': orders_last_7_days,
        
        # Статистика доходів
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_yesterday': revenue_yesterday,
        'revenue_last_7_days': revenue_last_7_days,
        
        # Статистика столиків
        'total_tables': total_tables,
        'occupied_tables': occupied_tables,
        'free_tables': free_tables,
        'reserved_tables': reserved_tables,
        
        # Популярні страви
        'popular_dishes': popular_dishes,
        
        # Активні замовлення
        'active_orders': active_orders,
        
        # Бронювання
        'upcoming_reservations': upcoming_reservations,
        'reservations_today': reservations_today,
        'reservations_tomorrow': reservations_tomorrow,
        
        # Запаси
        'low_stock_products': low_stock_products,
    })

@login_required
def sales_report(request):
    """Звіт з продажів за різні періоди"""
    
    # Отримуємо поточну дату та попередні періоди
    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Отримуємо дати з GET-запиту або використовуємо значення за замовчуванням
    period = request.GET.get('period', 'week')
    
    if period == 'today':
        start_date = today
        end_date = today
        title = f"Продажі за сьогодні ({today})"
    elif period == 'yesterday':
        start_date = today - datetime.timedelta(days=1)
        end_date = start_date
        title = f"Продажі за вчора ({start_date})"
    elif period == 'week':
        start_date = start_of_week
        end_date = today
        title = f"Продажі за поточний тиждень ({start_date} - {end_date})"
    elif period == 'month':
        start_date = start_of_month
        end_date = today
        title = f"Продажі за поточний місяць ({start_date} - {end_date})"
    elif period == 'custom':
        try:
            start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            title = f"Продажі за період ({start_date} - {end_date})"
        except (ValueError, TypeError):
            start_date = start_of_week
            end_date = today
            title = f"Продажі за поточний тиждень ({start_date} - {end_date})"
    else:
        start_date = start_of_week
        end_date = today
        title = f"Продажі за поточний тиждень ({start_date} - {end_date})"
    
    # Отримуємо всі замовлення за вибраний період
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    )
    
    # Рахуємо загальну статистику
    total_orders = orders.count()
    
    # Обчислюємо загальний дохід шляхом підсумовування всіх замовлень
    total_revenue = 0
    for order in orders:
        # Рахуємо суму кожного замовлення (ціна * кількість)
        order_total = sum(item.price * item.quantity for item in order.items.all())
        total_revenue += order_total
    
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Змінимо код для популярних страв
    popular_dishes = []
    # Словник для збору даних
    dish_data = {}
    
    # Збираємо дані вручну
    for order in orders:
        for item in order.items.all():
            dish_name = item.dish.name
            if dish_name not in dish_data:
                dish_data[dish_name] = {'count': 0, 'total_revenue': 0}
            
            dish_data[dish_name]['count'] += item.quantity
            dish_data[dish_name]['total_revenue'] += item.price * item.quantity
    
    # Перетворюємо словник на список
    for dish_name, data in dish_data.items():
        popular_dishes.append({
            'dish__name': dish_name,
            'count': data['count'],
            'total_revenue': data['total_revenue']
        })
    
    # Сортуємо за кількістю
    popular_dishes = sorted(popular_dishes, key=lambda x: x['count'], reverse=True)[:10]
    
    # Продажі за категоріями - теж вручну
    category_data = {}
    for order in orders:
        for item in order.items.all():
            category_name = item.dish.category.name if item.dish.category else "Без категорії"
            if category_name not in category_data:
                category_data[category_name] = {'count': 0, 'total_revenue': 0}
            
            category_data[category_name]['count'] += item.quantity
            category_data[category_name]['total_revenue'] += item.price * item.quantity
    
    # Перетворюємо словник на список
    sales_by_category = []
    for category_name, data in category_data.items():
        sales_by_category.append({
            'dish__category__name': category_name,
            'count': data['count'],
            'total_revenue': data['total_revenue']
        })
    
    # Сортуємо за доходом
    sales_by_category = sorted(sales_by_category, key=lambda x: x['total_revenue'], reverse=True)
    
    return render(request, 'dashboard/sales_report.html', {
        'title': title,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': average_order_value,
        'popular_dishes': popular_dishes,
        'sales_by_category': sales_by_category,
    })

@login_required
def tables_report(request):
    """Звіт із використання столиків"""
    
    # Отримуємо всі столики
    tables = Table.objects.filter(is_active=True).order_by('number')
    
    # Для кожного столика отримуємо статистику
    table_stats = []
    for table in tables:
        # Кількість замовлень для столика
        orders_count = Order.objects.filter(table=table).count()
        
        # Сума замовлень - обчислюємо вручну
        orders_sum = 0
        for order in Order.objects.filter(table=table):
            # Підраховуємо суму замовлення як суму всіх елементів
            order_total = sum(item.price * item.quantity for item in order.items.all())
            orders_sum += order_total
        
        # Кількість бронювань
        reservations_count = Reservation.objects.filter(table=table).count()
        
        table_stats.append({
            'table': table,
            'orders_count': orders_count,
            'orders_sum': orders_sum,
            'reservations_count': reservations_count,
            'average_order': orders_sum / orders_count if orders_count > 0 else 0,
        })
    
    # Сортуємо столики за сумою замовлень (найприбутковіші вгорі)
    table_stats.sort(key=lambda x: x['orders_sum'], reverse=True)
    
    return render(request, 'dashboard/tables_report.html', {
        'table_stats': table_stats,
    })