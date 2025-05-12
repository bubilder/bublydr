from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Загальні сторінки
    path('', views.order_list, name='list'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    
    # Створення та редагування замовлення
    path('create/', views.create_order, name='create'),
    path('<int:order_id>/edit/', views.edit_order, name='edit'),
    path('<int:order_id>/status/', views.change_order_status, name='change_status'),
    
    # Управління елементами замовлення
    path('<int:order_id>/add-item/', views.add_order_item, name='add_item'),
    path('<int:order_id>/remove-item/<int:item_id>/', views.remove_order_item, name='remove_item'),
    path('<int:order_id>/update-item/<int:item_id>/', views.update_order_item, name='update_item'),
    
    # Оплата та завершення
    path('<int:order_id>/complete/', views.complete_order, name='complete'),
    path('<int:order_id>/bill/', views.order_bill, name='bill'),
    path('mark-as-paid/<int:order_id>/', views.mark_as_paid, name='mark_as_paid'),
]