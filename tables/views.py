from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Table, Reservation
from .forms import TableForm, ReservationForm

def table_list(request):
    """Відображає список всіх столиків"""
    tables = Table.objects.filter(is_active=True)
    
    # Для кожного столика перевіряємо активне замовлення
    tables_with_orders = []
    for table in tables:
        active_order = None
        try:
            from orders.models import Order
            active_order = Order.objects.filter(
                table=table,
                status__in=['new', 'processing', 'ready', 'delivered']
            ).latest('created_at')
        except:
            pass
        
        tables_with_orders.append({
            'table': table,
            'active_order': active_order
        })
    
    return render(request, 'tables/list.html', {'tables_with_orders': tables_with_orders})

def table_detail(request, table_id):
    """Відображає деталі столика та його активне замовлення"""
    table = get_object_or_404(Table, id=table_id)
    
    # Шукаємо активне замовлення для цього столика
    # Активне замовлення - це замовлення, яке не завершене і не скасоване
    active_order = None
    try:
        from orders.models import Order
        active_order = Order.objects.filter(
            table=table,
            status__in=['new', 'processing', 'ready', 'delivered']
        ).latest('created_at')
    except:
        # Якщо активного замовлення немає або модуль замовлень не активний
        pass
    
    # Отримуємо минулі бронювання
    reservations = table.reservations.all().order_by('reservation_date', 'reservation_time')[:5]
    
    return render(request, 'tables/detail.html', {
        'table': table, 
        'active_order': active_order, 
        'reservations': reservations
    })

@login_required
def manage_tables(request):
    """Сторінка для керування всіма столиками (для персоналу)"""
    tables = Table.objects.all()
    return render(request, 'tables/manage.html', {'tables': tables})

@login_required
def create_table(request):
    """Створення нового столика"""
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save()
            messages.success(request, _('Столик успішно створено!'))
            return redirect('tables:detail', table_id=table.id)
    else:
        form = TableForm()
    
    return render(request, 'tables/form.html', {
        'form': form,
        'title': _('Створення нового столика')
    })

@login_required
def edit_table(request, table_id):
    """Редагування існуючого столика"""
    table = get_object_or_404(Table, id=table_id)
    
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, _('Столик успішно оновлено!'))
            return redirect('tables:detail', table_id=table.id)
    else:
        form = TableForm(instance=table)
    
    return render(request, 'tables/form.html', {
        'form': form,
        'table': table,
        'title': _('Редагування столика')
    })

@login_required
def reservation_list(request):
    """Відображає список бронювань"""
    reservations = Reservation.objects.all().order_by('-reservation_date', '-reservation_time')
    return render(request, 'tables/reservation_list.html', {'reservations': reservations})

@login_required
def create_reservation(request):
    """Створення нового бронювання"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            # Оновлення статусу столика
            table = reservation.table
            table.status = 'reserved'
            table.save()
            messages.success(request, _('Бронювання успішно створено!'))
            return redirect('tables:reservation_detail', reservation_id=reservation.id)
    else:
        # Перевіримо, чи передано столик через параметр запиту
        table_id = request.GET.get('table_id')
        if table_id:
            try:
                table = Table.objects.get(id=table_id, is_active=True)
                form = ReservationForm(initial={'table': table})
            except Table.DoesNotExist:
                form = ReservationForm()
        else:
            form = ReservationForm()
    
    return render(request, 'tables/reservation_form.html', {
        'form': form,
        'title': _('Створення нового бронювання')
    })

@login_required
def reservation_detail(request, reservation_id):
    """Відображає деталі бронювання"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    return render(request, 'tables/reservation_detail.html', {'reservation': reservation})

@login_required
def edit_reservation(request, reservation_id):
    """Редагування існуючого бронювання"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    old_status = reservation.status
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save()
            
            # Якщо статус змінився на "cancelled", оновлюємо статус столика
            if old_status != 'cancelled' and reservation.status == 'cancelled':
                table = reservation.table
                table.status = 'free'
                table.save()
            
            messages.success(request, _('Бронювання успішно оновлено!'))
            return redirect('tables:reservation_detail', reservation_id=reservation.id)
    else:
        form = ReservationForm(instance=reservation)
    
    return render(request, 'tables/reservation_form.html', {
        'form': form,
        'reservation': reservation,
        'title': _('Редагування бронювання')
    })