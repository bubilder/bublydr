from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Перегляд замовлень
    path('', views.order_list_view, name='list'),
    path('<int:pk>/', views.order_detail_view, name='detail'),
    
    # Управління замовленнями
    path('create/', views.order_create_view, name='create'),
    path('<int:pk>/edit/', views.order_edit_view, name='edit'),
    path('<int:pk>/status/', views.update_order_status_view, name='update_status'),
    path('<int:pk>/cancel/', views.cancel_order_view, name='cancel'),
    
    # Управління елементами замовлення
    path('<int:pk>/add-item/', views.add_item_to_order_view, name='add_item'),
    path('<int:order_pk>/remove-item/<int:item_pk>/', views.remove_item_from_order_view, name='remove_item'),
    
    # Оплата
    path('<int:pk>/payment/', views.payment_view, name='payment'),
]