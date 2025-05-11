from django.contrib import admin
from .models import Table, Reservation

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'location', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'capacity')
    search_fields = ('number', 'location', 'notes')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('table', 'customer_name', 'reservation_date', 'reservation_time', 'guests_count', 'status')
    list_filter = ('status', 'reservation_date')
    search_fields = ('customer_name', 'customer_phone', 'customer_email', 'notes')