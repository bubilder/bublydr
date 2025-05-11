from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('<int:payment_id>/', views.payment_detail, name='detail'),
    path('create/<int:order_id>/', views.create_payment, name='create'),
    path('complete/<int:payment_id>/', views.complete_payment, name='complete'),
    path('refund/<int:payment_id>/', views.refund_payment, name='refund'),
    path('receipt/<int:payment_id>/', views.generate_receipt, name='receipt'),
    path('receipt/<int:payment_id>/print/', views.print_receipt, name='print_receipt'),
    path('report/', views.payment_report, name='report'),
]