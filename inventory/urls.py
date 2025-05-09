from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list_view, name='list'),
    path('add/', views.ingredient_create_view, name='ingredient_add'),
    path('<int:pk>/', views.ingredient_detail_view, name='ingredient_detail'),
    path('<int:pk>/edit/', views.ingredient_update_view, name='ingredient_edit'),
    path('<int:pk>/delete/', views.ingredient_delete_view, name='ingredient_delete'),
    path('<int:pk>/add-stock/', views.add_stock_view, name='add_stock'),
    path('<int:pk>/remove-stock/', views.remove_stock_view, name='remove_stock'),
    path('transactions/', views.stock_transaction_list_view, name='transactions'),
]