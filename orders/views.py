from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm, OrderStatusForm
from tables.models import Table

@login_required
def order_list(request):
    """Відображає список всіх замовлень"""
    # Фільтри для статусів
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment')
    
    orders = Order.objects.all()
    
    # Застосовуємо фільтри
    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    if payment_filter and payment_filter != 'all':
        orders = orders.filter(payment_status=payment_filter)
    
    # Сортування за часом створення (спочатку найновіші)
    orders = orders.order_by('-created_at')
    
    return render(request, 'orders/list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    })

@login_required
def order_detail(request, order_id):
    """Відображає деталі замовлення"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def create_order(request):
    """Створення нового замовлення"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.waiter = request.user  # Поточний користувач як офіціант
            order.save()
            
            # Якщо столик раніше був вільний, позначаємо його як зайнятий
            if order.table and order.table.status == 'free':
                order.table.status = 'occupied'
                order.table.save()
                
            messages.success(request, _('Замовлення успішно створено!'))
            return redirect('orders:add_item', order_id=order.id)
    else:
        # Перевіряємо, чи передано столик через параметр запиту
        table_id = request.GET.get('table_id')
        initial_data = {}
        
        if table_id:
            try:
                table = Table.objects.get(id=table_id, is_active=True)
                initial_data = {'table': table}
            except Table.DoesNotExist:
                pass
                
        form = OrderForm(initial=initial_data)
    
    return render(request, 'orders/form.html', {
        'form': form,
        'title': _('Створення нового замовлення')
    })

@login_required
def edit_order(request, order_id):
    """Редагування існуючого замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status in ['completed', 'cancelled']:
        messages.error(request, _('Неможливо редагувати завершене або скасоване замовлення!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, _('Замовлення успішно оновлено!'))
            return redirect('orders:detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'orders/form.html', {
        'form': form,
        'order': order,
        'title': _('Редагування замовлення')
    })

@login_required
def change_order_status(request, order_id):
    """Зміна статусу замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            new_status = form.cleaned_data['status']
            
            # Зберігаємо форму
            order = form.save(commit=False)
            
            # Якщо статус зміниться на "завершено", встановлюємо час завершення
            if old_status != 'completed' and new_status == 'completed':
                order.completed_at = timezone.now()
            
            # Якщо замовлення скасовано і столик був зайнятий цим замовленням, звільняємо столик
            if new_status == 'cancelled' and order.table and order.table.status == 'occupied':
                order.table.status = 'free'
                order.table.save()
            
            order.save()
            messages.success(request, _('Статус замовлення успішно оновлено!'))
            return redirect('orders:detail', order_id=order.id)
    else:
        form = OrderStatusForm(instance=order)
    
    return render(request, 'orders/status_form.html', {
        'form': form,
        'order': order,
        'title': _('Зміна статусу замовлення')
    })

@login_required
def add_order_item(request, order_id):
    """Додавання страви до замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status in ['completed', 'cancelled']:
        messages.error(request, _('Неможливо додати страву до завершеного або скасованого замовлення!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            
            # Встановлюємо поточну ціну страви
            item.price = item.dish.price
            
            item.save()
            
            messages.success(request, _('Страву успішно додано до замовлення!'))
            
            # Повертаємось назад або додаємо ще одну страву
            if 'add_another' in request.POST:
                return redirect('orders:add_item', order_id=order.id)
            else:
                return redirect('orders:detail', order_id=order.id)
    else:
        form = OrderItemForm()
    
    return render(request, 'orders/item_form.html', {
        'form': form,
        'order': order,
        'title': _('Додавання страви до замовлення')
    })

@login_required
def update_order_item(request, order_id, item_id):
    """Оновлення елемента замовлення"""
    order = get_object_or_404(Order, id=order_id)
    item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if order.status in ['completed', 'cancelled']:
        messages.error(request, _('Неможливо оновити страву в завершеному або скасованому замовленні!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('Страву успішно оновлено!'))
            return redirect('orders:detail', order_id=order.id)
    else:
        form = OrderItemForm(instance=item)
    
    return render(request, 'orders/item_form.html', {
        'form': form,
        'order': order,
        'item': item,
        'title': _('Оновлення страви в замовленні')
    })

@login_required
def remove_order_item(request, order_id, item_id):
    """Видалення елемента замовлення"""
    order = get_object_or_404(Order, id=order_id)
    item = get_object_or_404(OrderItem, id=item_id, order=order)
    
    if order.status in ['completed', 'cancelled']:
        messages.error(request, _('Неможливо видалити страву з завершеного або скасованого замовлення!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, _('Страву успішно видалено з замовлення!'))
    
    return redirect('orders:detail', order_id=order.id)

@login_required
def complete_order(request, order_id):
    """Завершення замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'completed':
        messages.error(request, _('Замовлення вже завершено!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        order.mark_as_completed()
        
        # Якщо столик був зайнятий цим замовленням, звільняємо його
        if order.table and order.table.status == 'occupied':
            order.table.status = 'free'
            order.table.save()
        
        messages.success(request, _('Замовлення успішно завершено!'))
        
    return redirect('orders:detail', order_id=order.id)

@login_required
def order_bill(request, order_id):
    """Формування рахунку для замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    # Групуємо елементи замовлення за статусом (для рахунку потрібні тільки готові та доставлені)
    order_items = order.items.filter(status__in=['ready', 'delivered'])
    
    return render(request, 'orders/bill.html', {
        'order': order,
        'order_items': order_items,
    })