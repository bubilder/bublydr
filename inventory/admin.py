from django.contrib import admin
from .models import (
    Unit, ProductCategory, Product, Supplier, Purchase, PurchaseItem,
    Consumption, Recipe, RecipeIngredient
)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', 'short_name')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'current_quantity', 
                   'price_per_unit', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'barcode')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'notes')

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'created_at', 'expected_delivery')
    list_filter = ('status', 'supplier', 'created_at')
    search_fields = ('notes', 'invoice_number')
    readonly_fields = ('created_at', 'ordered_at', 'delivered_at')
    inlines = [PurchaseItemInline]

@admin.register(Consumption)
class ConsumptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reason', 'created_at', 'created_by')
    list_filter = ('reason', 'created_at')
    search_fields = ('product__name', 'notes')
    readonly_fields = ('created_at',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('dish', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('dish__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RecipeIngredientInline]