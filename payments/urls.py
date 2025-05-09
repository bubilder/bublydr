from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list_view, name='list'),
    path('<uuid:pk>/', views.receipt_view, name='receipt'),
    path('<uuid:pk>/pdf/', views.download_receipt_pdf, name='receipt_pdf'),
]