from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    # Перегляд столиків
    path('', views.table_list, name='list'),
    path('<int:table_id>/', views.table_detail, name='detail'),
    
    # Керування столиками (для персоналу)
    path('manage/', views.manage_tables, name='manage'),
    path('create/', views.create_table, name='create'),
    path('edit/<int:table_id>/', views.edit_table, name='edit'),
    
    # Бронювання
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.create_reservation, name='create_reservation'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
]