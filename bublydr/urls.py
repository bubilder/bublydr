from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from bublydr import views  # Змінено цей рядок з "from . import views"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Додай цей рядок для домашньої сторінки
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('tables/', include('tables.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('inventory/', include('inventory.urls')),
    path('dashboard/', include('dashboard.urls')),  # Додай цей рядок

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)