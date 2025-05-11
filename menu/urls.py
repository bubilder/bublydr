from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),
]