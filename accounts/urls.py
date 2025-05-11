from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.UpdateProfileView.as_view(), name='edit_profile'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('users/', views.users_list_view, name='users_list'),
]