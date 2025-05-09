from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm, OrderPaymentForm
from menu.models import Dish
from tables.models import Table
from payments.models import Payment

@login_required
def order_list_view(request):
    """Відображає список замовлень"""
    # Отримуємо статус з GET-параметрів або встановлюємо значення за замовчуванням
    status = request.GET.get('status', 'active')
    
    if status == 'active':
        orders = Order.objects.filter(
            status__in=['PENDING', 'IN_PROGRESS', 'READY', 'DELIVERED']
        ).order_by('-created_at')
    elif status == 'completed':
        orders = Order.objects.filter(status='COMPLETED').order_by('-created_at')
    elif status == 'canceled':
        orders = Order.objects.filter(status='CANCELED').order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')
    
    # Пошук
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) | 
            Q(table__number__icontains=search_query) | 
            Q(waiter__username__icontains=search_query)
        )
    
    # Пагінація
    paginator = Paginator(orders, 10)  # По 10 замовлень на сторінку
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status': status,
        'search_query': search_query,
    }
    
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail_view(request, pk):
    """Відображає деталі замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    # Перевіряємо, чи є пов'язаний платіж
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_create_view(request):
    """Створення нового замовлення"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.waiter = request.user
            order.save()
            
            # Оновлюємо статус столу
            table = order.table
            table.status = 'OCCUPIED'
            table.save()
            
            messages.success(request, _("Замовлення успішно створено"))
            return redirect('orders:edit', pk=order.pk)
    else:
        # Отримуємо тільки вільні столи
        free_tables = Table.objects.filter(status='FREE')
        form = OrderForm()
        form.fields['table'].queryset = free_tables
    
    return render(request, 'orders/order_form.html', {'form': form})

@login_required
def order_edit_view(request, pk):
    """Редагування замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    # Не дозволяємо редагувати завершені або скасовані замовлення
    if order.status in ['COMPLETED', 'CANCELED']:
        messages.warning(request, _("Неможливо редагувати завершене або скасоване замовлення"))
        return redirect('orders:detail', pk=order.pk)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, _("Замовлення успішно оновлено"))
            return redirect('orders:detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    
    # Отримуємо всі доступні страви для додавання до замовлення
    dishes = Dish.objects.filter(is_available=True)
    item_form = OrderItemForm()
    item_form.fields['dish'].queryset = dishes
    
    context = {
        'form': form,
        'order': order,
        'item_form': item_form,
    }
    
    return render(request, 'orders/order_edit.html', context)

@login_required
def add_item_to_order_view(request, pk):
    """Додавання страви до замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            dish = form.cleaned_data['dish']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            # Перевіряємо наявність страви
            if not dish.is_available:
                messages.error(request, _("Страва недоступна"))
                return redirect('orders:edit', pk=order.pk)
            
            # Додаємо страву до замовлення
            item = OrderItem(
                order=order,
                dish=dish,
                quantity=quantity,
                notes=notes,
                price=dish.price
            )
            item.save()
            
            messages.success(request, _("Страву додано до замовлення"))
        else:
            messages.error(request, _("Помилка при додаванні страви"))
    
    return redirect('orders:edit', pk=order.pk)

@login_required
def remove_item_from_order_view(request, order_pk, item_pk):
    """Видалення страви з замовлення"""
    order = get_object_or_404(Order, pk=order_pk)
    
    # Не дозволяємо редагувати завершені або скасовані замовлення
    if order.status in ['COMPLETED', 'CANCELED']:
        messages.warning(request, _("Неможливо редагувати завершене або скасоване замовлення"))
        return redirect('orders:detail', pk=order_pk)
    
    # Видаляємо елемент замовлення
    try:
        item = OrderItem.objects.get(pk=item_pk, order=order)
        item.delete()
        messages.success(request, _("Страву видалено з замовлення"))
    except OrderItem.DoesNotExist:
        messages.error(request, _("Елемент не знайдено"))
    
    return redirect('orders:edit', pk=order_pk)

@login_required
def update_order_status_view(request, pk):
    """Оновлення статусу замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [status[0] for status in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            
            messages.success(request, _("Статус замовлення оновлено"))
            
            # Якщо замовлення завершено, звільняємо стіл
            if new_status == 'COMPLETED' and order.is_paid:
                order.complete_order()
        else:
            messages.error(request, _("Недопустимий статус"))
    
    return redirect('orders:detail', pk=pk)

@login_required
def payment_view(request, pk):
    """Сторінка для оплати замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    # Якщо замовлення вже оплачене, перенаправляємо на сторінку деталей
    if order.is_paid:
        messages.info(request, _("Це замовлення вже оплачене"))
        return redirect('orders:detail', pk=pk)
    
    if request.method == 'POST':
        form = OrderPaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            amount_tendered = form.cleaned_data.get('amount_tendered')
            
            # Створюємо платіж
            payment = Payment(
                order=order,
                amount=order.total_price,
                payment_method=payment_method
            )
            
            # Якщо платіж готівкою, зберігаємо отриману суму
            if payment_method == 'CASH' and amount_tendered:
                payment.amount_tendered = amount_tendered
                payment.change_amount = amount_tendered - order.total_price
            
            payment.save()
            
            # Позначаємо замовлення як оплачене
            order.is_paid = True
            order.save()
            
            messages.success(request, _("Замовлення успішно оплачено"))
            
            # Перенаправляємо на сторінку чека
            return redirect('payments:receipt', pk=payment.pk)
    else:
        form = OrderPaymentForm()
    
    context = {
        'order': order,
        'form': form,
    }
    
    return render(request, 'orders/payment.html', context)

@login_required
def cancel_order_view(request, pk):
    """Скасування замовлення"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        # Перевіряємо, чи можна скасувати замовлення
        if order.status not in ['COMPLETED', 'CANCELED']:
            order.cancel_order()
            messages.success(request, _("Замовлення скасовано"))
        else:
            messages.error(request, _("Неможливо скасувати завершене або вже скасоване замовлення"))
    
    return redirect('orders:list')