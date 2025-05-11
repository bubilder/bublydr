from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'waiter', 'status', 'payment_status', 
                    'created_at', 'total_price')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'table__number', 'customer_name', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    inlines = [OrderItemInline]
    
    def total_price(self, obj):
        return f"{obj.total_price} грн"
    total_price.short_description = "Загальна сума"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'dish', 'quantity', 'price', 'subtotal', 'status')
    list_filter = ('status', 'order__status')
    search_fields = ('dish__name', 'order__id')
    
    def subtotal(self, obj):
        return f"{obj.subtotal} грн"
    subtotal.short_description = "Вартість"