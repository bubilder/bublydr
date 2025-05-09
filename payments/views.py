from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
from xhtml2pdf import pisa
import os

from .models import Payment

@login_required
def payment_list_view(request):
    """Відображає список всіх платежів (для адміністраторів)"""
    # Перевіряємо, чи є користувач адміністратором
    if not (request.user.role == 'ADMIN' or request.user.is_superuser):
        return redirect('dashboard:home')
    
    payments = Payment.objects.all().order_by('-created_at')
    
    context = {
        'payments': payments
    }
    
    return render(request, 'payments/payment_list.html', context)

@login_required
def receipt_view(request, pk):
    """Відображає чек для платежу"""
    payment = get_object_or_404(Payment, pk=pk)
    
    # Перевіряємо, чи може користувач бачити цей платіж
    # Адміністратори можуть бачити всі платежі, офіціанти - тільки свої
    if not (request.user.role == 'ADMIN' or request.user.is_superuser) and payment.order.waiter != request.user:
        return redirect('dashboard:home')
    
    context = {
        'payment': payment,
        'order': payment.order
    }
    
    return render(request, 'payments/receipt.html', context)

@login_required
def download_receipt_pdf(request, pk):
    """Генерує PDF-файл чека"""
    payment = get_object_or_404(Payment, pk=pk)
    
    # Перевіряємо доступ
    if not (request.user.role == 'ADMIN' or request.user.is_superuser) and payment.order.waiter != request.user:
        return redirect('dashboard:home')
    
    # Підготовка даних для шаблону
    context = {
        'payment': payment,
        'order': payment.order,
        'SITE_NAME': "Ресторан 'Смачного'"  # Назва ресторану
    }
    
    # Рендеринг HTML-шаблону
    template = get_template('payments/receipt_pdf.html')
    html = template.render(context)
    
    # Створення PDF з HTML
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
    
    # Генерація PDF
    pisa_status = pisa.CreatePDF(
        html, dest=response,
        encoding='utf-8'
    )
    
    if pisa_status.err:
        return HttpResponse('Виникла помилка при створенні PDF', content_type='text/plain')
    
    return response