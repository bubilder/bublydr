from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Перегляд меню для офіціантів
    path('', views.menu_list_view, name='list'),
    path('dish/<int:pk>/', views.dish_detail_view, name='dish_detail'),
    
    # Управління меню (адмін)
    path('manage/', views.menu_management_view, name='manage'),
    
    # Категорії
    path('category/add/', views.category_create_view, name='category_add'),
    path('category/<int:pk>/edit/', views.category_update_view, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
    
    # Страви
    path('dish/add/', views.dish_create_view, name='dish_add'),
    path('dish/<int:pk>/edit/', views.dish_update_view, name='dish_edit'),
    path('dish/<int:pk>/delete/', views.dish_delete_view, name='dish_delete'),
]