from rest_framework import serializers
from accounts.models import User
from menu.models import Category, Dish
from tables.models import Table
from orders.models import Order, OrderItem
from payments.models import Payment
from inventory.models import Ingredient

class UserSerializer(serializers.ModelSerializer):
    """Серіалізатор для користувачів"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    """Серіалізатор для категорій страв"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'order', 'is_active']

class DishSerializer(serializers.ModelSerializer):
    """Серіалізатор для страв"""
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name',
                  'image', 'is_available', 'preparation_time']

class TableSerializer(serializers.ModelSerializer):
    """Серіалізатор для столів"""
    status_display = serializers.ReadOnlyField(source='get_status_display')
    
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'status', 'status_display', 'location']

class OrderItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для елементів замовлення"""
    dish_name = serializers.ReadOnlyField(source='dish.name')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'dish', 'dish_name', 'quantity', 'price', 'notes', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для замовлень"""
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.ReadOnlyField(source='table.number')
    waiter_name = serializers.ReadOnlyField(source='waiter.get_full_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    
    class Meta:
        model = Order
        fields = ['id', 'table', 'table_number', 'waiter', 'waiter_name', 'status',
                  'status_display', 'created_at', 'updated_at', 'notes', 'is_paid',
                  'discount', 'items', 'subtotal_price', 'discount_amount', 'total_price']
        read_only_fields = ['id', 'created_at', 'updated_at', 'subtotal_price', 
                           'discount_amount', 'total_price']

class PaymentSerializer(serializers.ModelSerializer):
    """Серіалізатор для платежів"""
    order_id = serializers.ReadOnlyField(source='order.id')
    payment_method_display = serializers.ReadOnlyField(source='get_payment_method_display')
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'order_id', 'amount', 'payment_method',
                  'payment_method_display', 'amount_tendered', 'change_amount',
                  'transaction_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class IngredientSerializer(serializers.ModelSerializer):
    """Серіалізатор для інгредієнтів"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'description', 'current_stock', 'unit',
                  'minimum_stock', 'price_per_unit', 'is_low_stock', 'total_value']
        read_only_fields = ['id', 'is_low_stock', 'total_value']