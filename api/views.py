from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .serializers import (
    UserSerializer, CategorySerializer, DishSerializer, TableSerializer, 
    OrderSerializer, OrderItemSerializer, PaymentSerializer, IngredientSerializer
)
from accounts.models import User
from menu.models import Category, Dish
from tables.models import Table
from orders.models import Order, OrderItem
from payments.models import Payment
from inventory.models import Ingredient

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Користувацький дозвіл, що дозволяє тільки адміністраторам редагувати або створювати об'єкти.
    Інші ролі можуть тільки переглядати.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.role == 'ADMIN' or request.user.is_superuser)

class IsAdmin(permissions.BasePermission):
    """
    Користувацький дозвіл, що дозволяє доступ тільки адміністраторам.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'ADMIN' or request.user.is_superuser)

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint для користувачів"""
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Отримання інформації про поточного користувача"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint для категорій страв"""
    queryset = Category.objects.all().order_by('order')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def dishes(self, request, pk=None):
        """Отримання страв в категорії"""
        category = self.get_object()
        dishes = Dish.objects.filter(category=category)
        serializer = DishSerializer(dishes, many=True)
        return Response(serializer.data)

class DishViewSet(viewsets.ModelViewSet):
    """API endpoint для страв"""
    queryset = Dish.objects.all().order_by('category', 'name')
    serializer_class = DishSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Фільтрація страв за доступністю та категорією"""
        queryset = super().get_queryset()
        
        # Фільтрація за доступністю
        available = self.request.query_params.get('available')
        if available is not None:
            is_available = available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available)
        
        # Фільтрація за категорією
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset

class TableViewSet(viewsets.ModelViewSet):
    """API endpoint для столів"""
    queryset = Table.objects.all().order_by('number')
    serializer_class = TableSerializer
    
    def get_queryset(self):
        """Фільтрація столів за статусом"""
        queryset = super().get_queryset()
        
        # Фільтрація за статусом
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def active_order(self, request, pk=None):
        """Отримання активного замовлення для столу"""
        table = self.get_object()
        active_order = table.current_order
        
        if active_order:
            serializer = OrderSerializer(active_order)
            return Response(serializer.data)
        else:
            return Response({"detail": "Стіл не має активного замовлення."}, status=status.HTTP_404_NOT_FOUND)

class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint для замовлень"""
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Створення нового замовлення з призначенням поточного користувача як офіціанта"""
        data = request.data.copy()
        data['waiter'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Оновлюємо статус столу
        order = serializer.instance
        table = order.table
        table.status = 'OCCUPIED'
        table.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        """Фільтрація замовлень за статусом та офіціантом"""
        queryset = super().get_queryset()
        
        # Адміністратори бачать всі замовлення, офіціанти - тільки свої
        if self.request.user.role == 'WAITER':
            queryset = queryset.filter(waiter=self.request.user)
        
        # Фільтрація за статусом
        order_status = self.request.query_params.get('status')
        if order_status:
            if order_status == 'active':
                queryset = queryset.filter(
                    status__in=['PENDING', 'IN_PROGRESS', 'READY', 'DELIVERED']
                )
            else:
                queryset = queryset.filter(status=order_status)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Додавання страви до замовлення"""
        order = self.get_object()
        dish_id = request.data.get('dish')
        quantity = int(request.data.get('quantity', 1))
        notes = request.data.get('notes')
        
        # Перевіряємо, чи можна редагувати замовлення
        if order.status in ['COMPLETED', 'CANCELED']:
            return Response({"detail": "Неможливо редагувати завершене або скасоване замовлення"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Знаходимо страву
        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            return Response({"detail": "Страва не знайдена"}, status=status.HTTP_404_NOT_FOUND)
        
        # Перевіряємо доступність страви
        if not dish.is_available:
            return Response({"detail": "Страва недоступна"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Додаємо страву до замовлення
        item = OrderItem(
            order=order,
            dish=dish,
            quantity=quantity,
            price=dish.price,
            notes=notes
        )
        item.save()
        
        # Повертаємо оновлене замовлення
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """Видалення страви із замовлення"""
        order = self.get_object()
        
        # Перевіряємо, чи можна редагувати замовлення
        if order.status in ['COMPLETED', 'CANCELED']:
            return Response({"detail": "Неможливо редагувати завершене або скасоване замовлення"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Знаходимо елемент замовлення
        try:
            item = OrderItem.objects.get(id=item_id, order=order)
        except OrderItem.DoesNotExist:
            return Response({"detail": "Елемент замовлення не знайдений"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Видаляємо елемент
        item.delete()
        
        # Повертаємо оновлене замовлення
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Оновлення статусу замовлення"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        # Перевіряємо допустимість статусу
        if new_status not in [status for status, _ in Order.STATUS_CHOICES]:
            return Response({"detail": "Недопустимий статус"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Оновлюємо статус
        order.status = new_status
        order.save()
        
        # Якщо замовлення завершено і оплачено, звільняємо стіл
        if new_status == 'COMPLETED' and order.is_paid:
            order.complete_order()
        
        # Повертаємо оновлене замовлення
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Оплата замовлення"""
        order = self.get_object()
        
        # Перевіряємо, чи замовлення вже оплачене
        if order.is_paid:
            return Response({"detail": "Замовлення вже оплачене"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Отримуємо дані для оплати
        payment_method = request.data.get('payment_method')
        amount_tendered = request.data.get('amount_tendered')
        
        # Перевіряємо правильність даних
        if payment_method not in ['CASH', 'CARD']:
            return Response({"detail": "Недопустимий спосіб оплати"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Створюємо платіж
        payment = Payment(
            order=order,
            amount=order.total_price,
            payment_method=payment_method
        )
        
        # Якщо оплата готівкою, зберігаємо отриману суму та решту
        if payment_method == 'CASH' and amount_tendered:
            payment.amount_tendered = float(amount_tendered)
            payment.change_amount = float(amount_tendered) - float(order.total_price)
        
        payment.save()
        
        # Помічаємо замовлення як оплачене
        order.is_paid = True
        order.save()
        
        # Повертаємо дані про платіж
        payment_serializer = PaymentSerializer(payment)
        return Response(payment_serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint для платежів"""
    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Фільтрація платежів за офіціантом"""
        queryset = super().get_queryset()
        
        # Адміністратори бачать всі платежі, офіціанти - тільки свої
        if self.request.user.role == 'WAITER':
            queryset = queryset.filter(order__waiter=self.request.user)
        
        return queryset

class IngredientViewSet(viewsets.ModelViewSet):
    """API endpoint для інгредієнтів"""
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Додавання запасу інгредієнта"""
        ingredient = self.get_object()
        amount = float(request.data.get('amount', 0))
        unit_price = request.data.get('unit_price')
        notes = request.data.get('notes')
        
        if amount <= 0:
            return Response({"detail": "Кількість повинна бути більше 0"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Збільшуємо запас
        if unit_price:
            ingredient.increase_stock(amount, float(unit_price))
        else:
            ingredient.increase_stock(amount)
        
        # Повертаємо оновлений інгредієнт
        serializer = self.get_serializer(ingredient)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        """Видалення запасу інгредієнта"""
        ingredient = self.get_object()
        amount = float(request.data.get('amount', 0))
        notes = request.data.get('notes')
        
        if amount <= 0:
            return Response({"detail": "Кількість повинна бути більше 0"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if ingredient.current_stock < amount:
            return Response({"detail": "Недостатньо запасу"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Зменшуємо запас
        ingredient.decrease_stock(amount)
        
        # Повертаємо оновлений інгредієнт
        serializer = self.get_serializer(ingredient)
        return Response(serializer.data)

class OrderItemViewSet(viewsets.ModelViewSet):
    """API endpoint для елементів замовлення"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фільтрація за замовленням
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset