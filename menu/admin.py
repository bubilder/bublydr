from django.contrib import admin
from .models import Category, Dish

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_vegetarian', 'is_spicy')
    list_filter = ('category', 'is_available', 'is_vegetarian', 'is_spicy')
    search_fields = ('name', 'description')