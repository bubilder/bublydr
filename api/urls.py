from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

# Створюємо роутер для API
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'dishes', views.DishViewSet)
router.register(r'tables', views.TableViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'ingredients', views.IngredientViewSet)

app_name = 'api'

urlpatterns = [
    # API endpoints із роутера
    path('', include(router.urls)),
    
    # JWT аутентифікація
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API авторизація (для переглядача API)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]