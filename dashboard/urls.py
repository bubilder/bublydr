from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('sales/', views.sales_report, name='sales_report'),
    path('tables/', views.tables_report, name='tables_report'),
]