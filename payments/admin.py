from django.contrib import admin
from .models import Payment, Receipt

class ReceiptInline(admin.StackedInline):
    model = Receipt
    can_delete = False
    readonly_fields = ('receipt_number', 'fiscal_number', 'created_at', 'content')
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'payment_method', 'status', 
                   'created_at', 'cashier')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__id', 'transaction_id', 'notes')
    readonly_fields = ('created_at', 'completed_at')
    inlines = [ReceiptInline]

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'payment', 'created_at', 'is_printed')
    list_filter = ('is_printed', 'created_at')
    search_fields = ('receipt_number', 'fiscal_number', 'payment__order__id')
    readonly_fields = ('created_at',)