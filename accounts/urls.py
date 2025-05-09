from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', views.StaffCreateView.as_view(), name='staff_add'),
    path('staff/delete/<int:pk>/', views.staff_delete_view, name='staff_delete'),
]