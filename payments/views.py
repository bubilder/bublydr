from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import HttpResponse
import datetime
import random
import string

from .models import Payment, Receipt
from .forms import PaymentForm, PaymentFilterForm
from orders.models import Order

@login_required
def payment_list(request):
    """Відображає список всіх платежів з фільтрацією"""
    # Створюємо форму фільтрації
    filter_form = PaymentFilterForm(request.GET)
    
    # Початковий запит
    payments = Payment.objects.all()
    
    # Застосовуємо фільтри
    if filter_form.is_valid():
        # Фільтруємо за статусом
        if filter_form.cleaned_data.get('status'):
            payments = payments.filter(status=filter_form.cleaned_data['status'])
        
        # Фільтруємо за способом оплати
        if filter_form.cleaned_data.get('payment_method'):
            payments = payments.filter(payment_method=filter_form.cleaned_data['payment_method'])
        
        # Фільтруємо за датою (від)
        if filter_form.cleaned_data.get('date_from'):
            date_from = filter_form.cleaned_data['date_from']
            payments = payments.filter(created_at__date__gte=date_from)
        
        # Фільтруємо за датою (до)
        if filter_form.cleaned_data.get('date_to'):
            date_to = filter_form.cleaned_data['date_to']
            payments = payments.filter(created_at__date__lte=date_to)
    
    # Отримуємо загальну статистику
    total_amount = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    today = datetime.date.today()
    today_amount = payments.filter(status='completed', created_at__date=today).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    return render(request, 'payments/list.html', {
        'payments': payments,
        'filter_form': filter_form,
        'total_amount': total_amount,
        'today_amount': today_amount,
    })

@login_required
def payment_detail(request, payment_id):
    """Відображає деталі платежу"""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/detail.html', {'payment': payment})

@login_required
def create_payment(request, order_id):
    """Створення нового платежу для замовлення"""
    order = get_object_or_404(Order, id=order_id)
    
    # Перевіряємо, чи замовлення вже оплачене
    if order.payment_status == 'paid':
        messages.error(request, _('Це замовлення вже оплачене!'))
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, order=order)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.cashier = request.user
            payment.save()
            
            # Якщо користувач натиснув "Оплатити зараз", відразу завершуємо платіж
            if 'complete_now' in request.POST:
                payment.complete()
                
                # Створюємо чек для платежу
                receipt = Receipt.objects.create(
                    payment=payment,
                    receipt_number=generate_receipt_number(),
                )
                receipt.generate_content()
                
                messages.success(request, _('Платіж успішно завершено і чек створено!'))
                return redirect('payments:receipt', payment_id=payment.id)
            else:
                messages.success(request, _('Платіж успішно створено!'))
                return redirect('payments:detail', payment_id=payment.id)
    else:
        # За замовчуванням встановлюємо суму рівною сумі замовлення
        initial = {'amount': order.total_price}
        form = PaymentForm(initial=initial, order=order)
    
    return render(request, 'payments/form.html', {
        'form': form,
        'order': order,
        'title': _('Створення нового платежу')
    })

@login_required
def complete_payment(request, payment_id):
    """Завершення платежу"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'completed':
        messages.error(request, _('Цей платіж вже завершено!'))
        return redirect('payments:detail', payment_id=payment.id)
    
    if request.method == 'POST':
        payment.complete()
        
        # Створюємо чек для платежу, якщо його ще немає
        try:
            receipt = payment.receipt
        except Receipt.DoesNotExist:
            receipt = Receipt.objects.create(
                payment=payment,
                receipt_number=generate_receipt_number(),
            )
            receipt.generate_content()
        
        messages.success(request, _('Платіж успішно завершено!'))
        return redirect('payments:receipt', payment_id=payment.id)
    
    return render(request, 'payments/confirm_action.html', {
        'payment': payment,
        'title': _('Підтвердження завершення платежу'),
        'message': _('Ви дійсно хочете завершити цей платіж?'),
        'action': _('Завершити платіж'),
        'action_url': reverse('payments:complete', args=[payment.id])
    })

@login_required
def refund_payment(request, payment_id):
    """Повернення платежу"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status in ['refunded', 'failed']:
        messages.error(request, _('Цей платіж вже повернуто або він не був успішним!'))
        return redirect('payments:detail', payment_id=payment.id)
    
    if request.method == 'POST':
        payment.refund()
        messages.success(request, _('Платіж успішно повернуто!'))
        return redirect('payments:detail', payment_id=payment.id)
    
    return render(request, 'payments/confirm_action.html', {
        'payment': payment,
        'title': _('Підтвердження повернення платежу'),
        'message': _('Ви дійсно хочете повернути цей платіж?'),
        'action': _('Повернути платіж'),
        'action_url': reverse('payments:refund', args=[payment.id])
    })

@login_required
def generate_receipt(request, payment_id):
    """Формування чека для платежу"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Отримуємо або створюємо чек для платежу
    try:
        receipt = payment.receipt
    except Receipt.DoesNotExist:
        receipt = Receipt.objects.create(
            payment=payment,
            receipt_number=generate_receipt_number(),
        )
    
    # Генеруємо вміст чека
    receipt.generate_content()
    
    return render(request, 'payments/receipt.html', {
        'payment': payment,
        'receipt': receipt,
    })

@login_required
def print_receipt(request, payment_id):
    """Друк чека"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    try:
        receipt = payment.receipt
    except Receipt.DoesNotExist:
        messages.error(request, _('Чек для цього платежу не знайдено!'))
        return redirect('payments:detail', payment_id=payment.id)
    
    # Позначаємо чек як надрукований
    receipt.mark_as_printed()
    
    # В реальному проєкті тут була б інтеграція з принтером
    # Для прикладу просто повертаємо текстовий вміст чека
    response = HttpResponse(receipt.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.txt"'
    
    return response

@login_required
def payment_report(request):
    """Формування звіту по платежах"""
    # За останні 30 днів
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    # Отримуємо дані для звіту
    payments = Payment.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    )
    
    # Групуємо за днями
    daily_stats = {}
    for payment in payments:
        day = payment.created_at.date()
        if day not in daily_stats:
            daily_stats[day] = {
                'date': day,
                'count': 0,
                'total': 0,
                'cash': 0,
                'card': 0,
                'online': 0,
                'transfer': 0,
            }
        
        daily_stats[day]['count'] += 1
        daily_stats[day]['total'] += payment.amount
        
        # Збільшуємо суму відповідного способу оплати
        if payment.payment_method == 'cash':
            daily_stats[day]['cash'] += payment.amount
        elif payment.payment_method == 'card':
            daily_stats[day]['card'] += payment.amount
        elif payment.payment_method == 'online':
            daily_stats[day]['online'] += payment.amount
        elif payment.payment_method == 'transfer':
            daily_stats[day]['transfer'] += payment.amount
    
    # Сортуємо за датою (найновіші спочатку)
    daily_stats_sorted = sorted(daily_stats.values(), key=lambda x: x['date'], reverse=True)
    
    # Загальна статистика
    total_payments = payments.count()
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    payment_methods_stats = payments.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    return render(request, 'payments/report.html', {
        'daily_stats': daily_stats_sorted,
        'total_payments': total_payments,
        'total_amount': total_amount,
        'payment_methods_stats': payment_methods_stats,
        'start_date': start_date,
        'end_date': end_date,
    })

def generate_receipt_number():
    """Генерує унікальний номер чека"""
    prefix = datetime.datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{random_suffix}"