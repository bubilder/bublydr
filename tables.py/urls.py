from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    # Перегляд столів
    path('', views.table_list_view, name='list'),
    path('<int:pk>/', views.table_detail_view, name='detail'),
    path('<int:table_id>/order/create/', views.create_order_for_table, name='create_order'),
    
    # Управління столами (адмін)
    path('add/', views.table_create_view, name='add'),
    path('<int:pk>/edit/', views.table_update_view, name='edit'),
    path('<int:pk>/delete/', views.table_delete_view, name='delete'),
    
    # Резервації
    path('reservations/', views.reservation_list_view, name='reservations'),
    path('reservations/add/', views.reservation_create_view, name='reservation_add'),
    path('reservations/<int:pk>/delete/', views.reservation_delete_view, name='reservation_delete'),
]