from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Налаштування Swagger документації API
schema_view = get_schema_view(
    openapi.Info(
        title="Bublydr POS API",  # Змінено з "Restaurant POS API"
        default_version='v1',
        description="API для ресторанної POS-системи",
        contact=openapi.Contact(email="admin@bublydr.com"),  # Змінено email
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('tables/', include('tables.urls')),
    path('payments/', include('payments.urls')),
    path('inventory/', include('inventory.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('api/', include('api.urls')),
    
    # Swagger документація
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Головна сторінка
    path('', include('dashboard.urls')),
]

# Для медіа файлів у режимі розробки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)