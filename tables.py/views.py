from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Table, Reservation
from .forms import TableForm, ReservationForm
from orders.models import Order

def is_admin(user):
    """Перевірка чи користувач є адміністратором"""
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@login_required
def table_list_view(request):
    """Перегляд усіх столів з їх статусом"""
    tables = Table.objects.all().order_by('number')
    return render(request, 'tables/table_list.html', {'tables': tables})

@login_required
def table_detail_view(request, pk):
    """Детальна інформація про стіл з можливістю створення замовлення"""
    table = get_object_or_404(Table, pk=pk)
    
    # Отримуємо активне замовлення для столу, якщо таке є
    active_order = table.current_order
    
    # Отримуємо сьогоднішні резервації для цього столу
    today = timezone.now().date()
    reservations = table.reservations.filter(reservation_date=today)
    
    context = {
        'table': table,
        'active_order': active_order,
        'reservations': reservations,
    }
    
    return render(request, 'tables/table_detail.html', context)

@login_required
def create_order_for_table(request, table_id):
    """Створення нового замовлення для столу"""
    table = get_object_or_404(Table, pk=table_id)
    
    # Перевіряємо чи стіл вже має активне замовлення
    if table.current_order:
        messages.warning(request, _("Цей стіл вже має активне замовлення"))
        return redirect('tables:detail', pk=table_id)
    
    # Створюємо нове замовлення
    order = Order.objects.create(
        table=table,
        waiter=request.user,
        status='PENDING'
    )
    
    # Оновлюємо статус столу
    table.set_status('OCCUPIED')
    
    messages.success(request, _("Нове замовлення створено"))
    return redirect('orders:edit', pk=order.pk)

@user_passes_test(is_admin)
def table_create_view(request):
    """Створення нового столу (тільки для адміністраторів)"""
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Стіл успішно створено"))
            return redirect('tables:list')
    else:
        form = TableForm()
    
    return render(request, 'tables/table_form.html', {'form': form})

@user_passes_test(is_admin)
def table_update_view(request, pk):
    """Редагування столу (тільки для адміністраторів)"""
    table = get_object_or_404(Table, pk=pk)
    
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, _("Інформацію про стіл оновлено"))
            return redirect('tables:list')
    else:
        form = TableForm(instance=table)
    
    return render(request, 'tables/table_form.html', {'form': form, 'table': table})

@user_passes_test(is_admin)
def table_delete_view(request, pk):
    """Видалення столу (тільки для адміністраторів)"""
    table = get_object_or_404(Table, pk=pk)
    
    if request.method == 'POST':
        if table.orders.filter(status__in=['PENDING', 'IN_PROGRESS']).exists():
            messages.error(request, _("Неможливо видалити стіл з активними замовленнями"))
            return redirect('tables:list')
        
        table.delete()
        messages.success(request, _("Стіл успішно видалено"))
        return redirect('tables:list')
    
    return render(request, 'tables/table_confirm_delete.html', {'table': table})

@login_required
def reservation_create_view(request):
    """Створення резервації столу"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            messages.success(request, _("Резервацію успішно створено"))
            return redirect('tables:detail', pk=reservation.table.pk)
    else:
        form = ReservationForm()
    
    return render(request, 'tables/reservation_form.html', {'form': form})

@login_required
def reservation_list_view(request):
    """Перегляд усіх резервацій"""
    today = timezone.now().date()
    upcoming_reservations = Reservation.objects.filter(reservation_date__gte=today).order_by('reservation_date', 'reservation_time')
    past_reservations = Reservation.objects.filter(reservation_date__lt=today).order_by('-reservation_date', 'reservation_time')
    
    return render(request, 'tables/reservation_list.html', {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations
    })

@login_required
def reservation_delete_view(request, pk):
    """Видалення резервації"""
    reservation = get_object_or_404(Reservation, pk=pk)
    table = reservation.table
    
    if request.method == 'POST':
        reservation.delete()
        
        # Перевірка чи є ще резервації для цього столу на сьогодні
        today = timezone.now().date()
        if not table.reservations.filter(reservation_date=today).exists():
            # Якщо немає інших резервацій, оновлюємо статус столу
            table.set_status('FREE')
            
        messages.success(request, _("Резервацію скасовано"))
        return redirect('tables:reservations')
    
    return render(request, 'tables/reservation_confirm_delete.html', {'reservation': reservation})