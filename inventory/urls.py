from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Продукти
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    
    # Категорії продуктів
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    
    # Одиниці виміру
    path('units/', views.unit_list, name='unit_list'),
    path('units/add/', views.unit_add, name='unit_add'),
    path('units/<int:unit_id>/edit/', views.unit_edit, name='unit_edit'),
    
    # Постачальники
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    
    # Закупівлі
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.purchase_add, name='purchase_add'),
    path('purchases/<int:purchase_id>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:purchase_id>/edit/', views.purchase_edit, name='purchase_edit'),
    path('purchases/<int:purchase_id>/add-item/', views.purchase_add_item, name='purchase_add_item'),
    path('purchases/<int:purchase_id>/remove-item/<int:item_id>/', views.purchase_remove_item, name='purchase_remove_item'),
    path('purchases/<int:purchase_id>/order/', views.purchase_order, name='purchase_order'),
    path('purchases/<int:purchase_id>/receive/', views.purchase_receive, name='purchase_receive'),
    path('purchases/<int:purchase_id>/cancel/', views.purchase_cancel, name='purchase_cancel'),
    
    # Списання
    path('consumptions/', views.consumption_list, name='consumption_list'),
    path('consumptions/add/', views.consumption_add, name='consumption_add'),
    
    # Рецепти
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/add/', views.recipe_add, name='recipe_add'),
    path('recipes/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipes/<int:recipe_id>/add-ingredient/', views.recipe_add_ingredient, name='recipe_add_ingredient'),
    path('recipes/<int:recipe_id>/remove-ingredient/<int:ingredient_id>/', views.recipe_remove_ingredient, name='recipe_remove_ingredient'),
    
    # Звіти
    path('reports/inventory-value/', views.report_inventory_value, name='report_inventory_value'),
    path('reports/low-stock/', views.report_low_stock, name='report_low_stock'),
    path('reports/consumptions/', views.report_consumptions, name='report_consumptions'),
    
    # Головна сторінка модуля
    path('', views.inventory_dashboard, name='dashboard'),
]