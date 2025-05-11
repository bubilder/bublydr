from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone

from decimal import Decimal
import datetime

from .models import (
    Unit, ProductCategory, Product, Supplier, Purchase, PurchaseItem,
    Consumption, Recipe, RecipeIngredient
)
from .forms import (
    UnitForm, ProductCategoryForm, ProductForm, SupplierForm, PurchaseForm,
    PurchaseItemForm, ConsumptionForm, RecipeForm, RecipeIngredientForm,
    ProductFilterForm
)

@login_required
def inventory_dashboard(request):
    """Головна сторінка модуля інвентаризації"""
    # Отримуємо загальну статистику
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(
        is_active=True, 
        current_quantity__lt=F('minimum_quantity')
    ).count()
    
    # Загальна вартість запасів
    total_value_expr = ExpressionWrapper(
        F('current_quantity') * F('price_per_unit'), 
        output_field=DecimalField()
    )
    total_value = Product.objects.filter(is_active=True).annotate(
        value=total_value_expr
    ).aggregate(total=Sum('value'))['total'] or 0
    
    # Нещодавні закупівлі
    recent_purchases = Purchase.objects.order_by('-created_at')[:5]
    
    # Нещодавні списання
    recent_consumptions = Consumption.objects.order_by('-created_at')[:5]
    
    # Продукти з критично низьким запасом
    low_stock_products = Product.objects.filter(
        is_active=True, 
        current_quantity__lt=F('minimum_quantity')
    ).order_by('category__name', 'name')[:10]
    
    return render(request, 'inventory/dashboard.html', {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_value': total_value,
        'recent_purchases': recent_purchases,
        'recent_consumptions': recent_consumptions,
        'low_stock_products': low_stock_products,
    })

# ПРОДУКТИ

@login_required
def product_list(request):
    """Відображає список всіх продуктів з фільтрацією"""
    # Створюємо форму фільтрації
    filter_form = ProductFilterForm(request.GET)
    
    # Початковий запит
    products = Product.objects.all()
    
    # Застосовуємо фільтри
    if filter_form.is_valid():
        # Фільтруємо за категорією
        if filter_form.cleaned_data.get('category'):
            products = products.filter(category=filter_form.cleaned_data['category'])
        
        # Фільтруємо за низьким запасом
        if filter_form.cleaned_data.get('low_stock_only'):
            products = products.filter(current_quantity__lt=F('minimum_quantity'))
        
        # Фільтруємо за пошуковим запитом
        if filter_form.cleaned_data.get('search'):
            search_query = filter_form.cleaned_data['search']
            products = products.filter(name__icontains=search_query)
    
    # Додаємо обчислюване поле для загальної вартості кожного продукту
    total_value_expr = ExpressionWrapper(
        F('current_quantity') * F('price_per_unit'), 
        output_field=DecimalField()
    )
    products = products.annotate(total_value=total_value_expr)
    
    # Сортуємо за категорією та назвою
    products = products.order_by('category__name', 'name')
    
    return render(request, 'inventory/product_list.html', {
        'products': products,
        'filter_form': filter_form,
    })

@login_required
def product_detail(request, product_id):
    """Відображає детальну інформацію про продукт"""
    product = get_object_or_404(Product, id=product_id)
    
    # Отримуємо історію закупівель та списань цього продукту
    purchase_items = PurchaseItem.objects.filter(product=product).order_by('-purchase__created_at')
    consumptions = Consumption.objects.filter(product=product).order_by('-created_at')
    
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'purchase_items': purchase_items,
        'consumptions': consumptions,
    })

@login_required
def product_add(request):
    """Додавання нового продукту"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, _('Продукт успішно створено!'))
            return redirect('inventory:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'title': _('Додавання нового продукту'),
    })

@login_required
def product_edit(request, product_id):
    """Редагування існуючого продукту"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, _('Продукт успішно оновлено!'))
            return redirect('inventory:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'product': product,
        'title': _('Редагування продукту'),
    })

# КАТЕГОРІЇ ПРОДУКТІВ

@login_required
def category_list(request):
    """Відображає список всіх категорій продуктів"""
    categories = ProductCategory.objects.all().order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    """Додавання нової категорії продуктів"""
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, _('Категорію продуктів успішно створено!'))
            return redirect('inventory:category_list')
    else:
        form = ProductCategoryForm()
    
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'title': _('Додавання нової категорії продуктів'),
    })

@login_required
def category_edit(request, category_id):
    """Редагування існуючої категорії продуктів"""
    category = get_object_or_404(ProductCategory, id=category_id)
    
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Категорію продуктів успішно оновлено!'))
            return redirect('inventory:category_list')
    else:
        form = ProductCategoryForm(instance=category)
    
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'category': category,
        'title': _('Редагування категорії продуктів'),
    })

# ОДИНИЦІ ВИМІРУ

@login_required
def unit_list(request):
    """Відображає список всіх одиниць виміру"""
    units = Unit.objects.all().order_by('name')
    return render(request, 'inventory/unit_list.html', {'units': units})

@login_required
def unit_add(request):
    """Додавання нової одиниці виміру"""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, _('Одиницю виміру успішно створено!'))
            return redirect('inventory:unit_list')
    else:
        form = UnitForm()
    
    return render(request, 'inventory/unit_form.html', {
        'form': form,
        'title': _('Додавання нової одиниці виміру'),
    })

@login_required
def unit_edit(request, unit_id):
    """Редагування існуючої одиниці виміру"""
    unit = get_object_or_404(Unit, id=unit_id)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, _('Одиницю виміру успішно оновлено!'))
            return redirect('inventory:unit_list')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'inventory/unit_form.html', {
        'form': form,
        'unit': unit,
        'title': _('Редагування одиниці виміру'),
    })

# ПОСТАЧАЛЬНИКИ

@login_required
def supplier_list(request):
    """Відображає список всіх постачальників"""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_detail(request, supplier_id):
    """Відображає детальну інформацію про постачальника"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    # Отримуємо історію закупівель від цього постачальника
    purchases = Purchase.objects.filter(supplier=supplier).order_by('-created_at')
    
    return render(request, 'inventory/supplier_detail.html', {
        'supplier': supplier,
        'purchases': purchases,
    })

@login_required
def supplier_add(request):
    """Додавання нового постачальника"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, _('Постачальника успішно створено!'))
            return redirect('inventory:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': _('Додавання нового постачальника'),
    })

@login_required
def supplier_edit(request, supplier_id):
    """Редагування існуючого постачальника"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, _('Постачальника успішно оновлено!'))
            return redirect('inventory:supplier_detail', supplier_id=supplier.id)
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'supplier': supplier,
        'title': _('Редагування постачальника'),
    })

# ЗАКУПІВЛІ

@login_required
def purchase_list(request):
    """Відображає список всіх закупівель"""
    purchases = Purchase.objects.all().order_by('-created_at')
    return render(request, 'inventory/purchase_list.html', {'purchases': purchases})

@login_required
def purchase_detail(request, purchase_id):
    """Відображає детальну інформацію про закупівлю"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    return render(request, 'inventory/purchase_detail.html', {'purchase': purchase})

@login_required
def purchase_add(request):
    """Створення нової закупівлі"""
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            
            messages.success(request, _('Закупівлю успішно створено!'))
            return redirect('inventory:purchase_add_item', purchase_id=purchase.id)
    else:
        form = PurchaseForm()
    
    return render(request, 'inventory/purchase_form.html', {
        'form': form,
        'title': _('Створення нової закупівлі'),
    })

@login_required
def purchase_edit(request, purchase_id):
    """Редагування існуючої закупівлі"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if purchase.status != 'pending':
        messages.error(request, _('Неможливо редагувати закупівлю, яка вже не в статусі "Очікується"!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, _('Закупівлю успішно оновлено!'))
            return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    else:
        form = PurchaseForm(instance=purchase)
    
    return render(request, 'inventory/purchase_form.html', {
        'form': form,
        'purchase': purchase,
        'title': _('Редагування закупівлі'),
    })

@login_required
def purchase_add_item(request, purchase_id):
    """Додавання продукту до закупівлі"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if purchase.status != 'pending':
        messages.error(request, _('Неможливо додавати продукти до закупівлі, яка вже не в статусі "Очікується"!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST)
        if form.is_valid():
            purchase_item = form.save(commit=False)
            purchase_item.purchase = purchase
            
            # Перевіряємо, чи цей продукт вже є в закупівлі
            existing_item = PurchaseItem.objects.filter(
                purchase=purchase,
                product=purchase_item.product
            ).first()
            
            if existing_item:
                # Якщо продукт вже є, оновлюємо кількість
                existing_item.quantity += purchase_item.quantity
                existing_item.save()
                messages.success(request, _('Кількість продукту успішно оновлено!'))
            else:
                # Якщо продукту немає, додаємо новий
                purchase_item.save()
                messages.success(request, _('Продукт успішно додано до закупівлі!'))
            
            # Повертаємося назад або додаємо ще один продукт
            if 'add_another' in request.POST:
                return redirect('inventory:purchase_add_item', purchase_id=purchase.id)
            else:
                return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    else:
        form = PurchaseItemForm()
    
    return render(request, 'inventory/purchase_item_form.html', {
        'form': form,
        'purchase': purchase,
        'title': _('Додавання продукту до закупівлі'),
    })

@login_required
def purchase_remove_item(request, purchase_id, item_id):
    """Видалення продукту з закупівлі"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    item = get_object_or_404(PurchaseItem, id=item_id, purchase=purchase)
    
    if purchase.status != 'pending':
        messages.error(request, _('Неможливо видаляти продукти з закупівлі, яка вже не в статусі "Очікується"!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, _('Продукт успішно видалено з закупівлі!'))
    
    return redirect('inventory:purchase_detail', purchase_id=purchase.id)

@login_required
def purchase_order(request, purchase_id):
    """Позначає закупівлю як замовлену"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if purchase.status != 'pending':
        messages.error(request, _('Неможливо замовити закупівлю, яка вже не в статусі "Очікується"!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if not purchase.items.exists():
        messages.error(request, _('Неможливо замовити закупівлю без продуктів!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        purchase.mark_as_ordered()
        messages.success(request, _('Закупівлю успішно позначено як замовлену!'))
    
    return redirect('inventory:purchase_detail', purchase_id=purchase.id)

@login_required
def purchase_receive(request, purchase_id):
    """Позначає закупівлю як доставлену"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if purchase.status != 'ordered':
        messages.error(request, _('Неможливо отримати закупівлю, яка не в статусі "Замовлено"!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        purchase.mark_as_delivered()
        messages.success(request, _('Закупівлю успішно позначено як отриману, кількості продуктів оновлено!'))
    
    return redirect('inventory:purchase_detail', purchase_id=purchase.id)

@login_required
def purchase_cancel(request, purchase_id):
    """Скасовує закупівлю"""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if purchase.status not in ['pending', 'ordered']:
        messages.error(request, _('Неможливо скасувати закупівлю в поточному статусі!'))
        return redirect('inventory:purchase_detail', purchase_id=purchase.id)
    
    if request.method == 'POST':
        purchase.mark_as_cancelled()
        messages.success(request, _('Закупівлю успішно скасовано!'))
    
    return redirect('inventory:purchase_detail', purchase_id=purchase.id)

# СПИСАННЯ

@login_required
def consumption_list(request):
    """Відображає список всіх списань"""
    consumptions = Consumption.objects.all().order_by('-created_at')
    return render(request, 'inventory/consumption_list.html', {'consumptions': consumptions})

@login_required
def consumption_add(request):
    """Створення нового списання"""
    if request.method == 'POST':
        form = ConsumptionForm(request.POST)
        if form.is_valid():
            consumption = form.save(commit=False)
            consumption.created_by = request.user
            consumption.save()
            
            messages.success(request, _('Списання успішно створено!'))
            
            # Повертаємося назад або створюємо ще одне списання
            if 'add_another' in request.POST:
                return redirect('inventory:consumption_add')
            else:
                return redirect('inventory:consumption_list')
    else:
        form = ConsumptionForm()
    
    return render(request, 'inventory/consumption_form.html', {
        'form': form,
        'title': _('Створення нового списання'),
    })

# РЕЦЕПТИ

@login_required
def recipe_list(request):
    """Відображає список всіх рецептів"""
    recipes = Recipe.objects.all().order_by('dish__name')
    return render(request, 'inventory/recipe_list.html', {'recipes': recipes})

@login_required
def recipe_detail(request, recipe_id):
    """Відображає детальну інформацію про рецепт"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    return render(request, 'inventory/recipe_detail.html', {'recipe': recipe})

@login_required
def recipe_add(request):
    """Створення нового рецепту"""
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, _('Рецепт успішно створено!'))
            return redirect('inventory:recipe_add_ingredient', recipe_id=recipe.id)
    else:
        form = RecipeForm()
    
    return render(request, 'inventory/recipe_form.html', {
        'form': form,
        'title': _('Створення нового рецепту'),
    })

@login_required
def recipe_edit(request, recipe_id):
    """Редагування існуючого рецепту"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            messages.success(request, _('Рецепт успішно оновлено!'))
            return redirect('inventory:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    
    return render(request, 'inventory/recipe_form.html', {
        'form': form,
        'recipe': recipe,
        'title': _('Редагування рецепту'),
    })

@login_required
def recipe_add_ingredient(request, recipe_id):
    """Додавання інгредієнта до рецепту"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            
            # Перевіряємо, чи цей інгредієнт вже є в рецепті
            existing_ingredient = RecipeIngredient.objects.filter(
                recipe=recipe,
                product=ingredient.product
            ).first()
            
            if existing_ingredient:
                # Якщо інгредієнт вже є, оновлюємо кількість
                existing_ingredient.quantity += ingredient.quantity
                existing_ingredient.save()
                messages.success(request, _('Кількість інгредієнта успішно оновлено!'))
            else:
                # Якщо інгредієнта немає, додаємо новий
                ingredient.save()
                messages.success(request, _('Інгредієнт успішно додано до рецепту!'))
            
            # Повертаємося назад або додаємо ще один інгредієнт
            if 'add_another' in request.POST:
                return redirect('inventory:recipe_add_ingredient', recipe_id=recipe.id)
            else:
                return redirect('inventory:recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeIngredientForm()
    
    return render(request, 'inventory/recipe_ingredient_form.html', {
        'form': form,
        'recipe': recipe,
        'title': _('Додавання інгредієнта до рецепту'),
    })

@login_required
def recipe_remove_ingredient(request, recipe_id, ingredient_id):
    """Видалення інгредієнта з рецепту"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredient = get_object_or_404(RecipeIngredient, id=ingredient_id, recipe=recipe)
    
    if request.method == 'POST':
        ingredient.delete()
        messages.success(request, _('Інгредієнт успішно видалено з рецепту!'))
    
    return redirect('inventory:recipe_detail', recipe_id=recipe.id)

# ЗВІТИ

@login_required
def report_inventory_value(request):
    """Звіт про вартість запасів"""
    # Групуємо продукти за категоріями
    categories = ProductCategory.objects.all().order_by('name')
    report_data = []
    
    total_value = Decimal('0')
    
    for category in categories:
        products = Product.objects.filter(category=category, is_active=True)
        
        category_data = {
            'category': category,
            'products': [],
            'total': Decimal('0')
        }
        
        for product in products:
            value = product.current_quantity * product.price_per_unit
            category_data['products'].append({
                'product': product,
                'value': value
            })
            category_data['total'] += value
            total_value += value
        
        if category_data['products']:
            report_data.append(category_data)
    
    return render(request, 'inventory/report_inventory_value.html', {
        'report_data': report_data,
        'total_value': total_value,
        'date_generated': timezone.now()
    })

@login_required
def report_low_stock(request):
    """Звіт про продукти з низьким рівнем запасів"""
    low_stock_products = Product.objects.filter(
        is_active=True, 
        current_quantity__lt=F('minimum_quantity')
    ).order_by('category__name', 'name')
    
    return render(request, 'inventory/report_low_stock.html', {
        'products': low_stock_products,
        'date_generated': timezone.now()
    })

@login_required
def report_consumptions(request):
    """Звіт про списання продуктів"""
    # За останні 30 днів
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    consumptions = Consumption.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).order_by('-created_at')
    
    # Групуємо за причиною списання
    reasons_data = {}
    for reason_code, reason_display in Consumption.REASON_CHOICES:
        reason_consumptions = consumptions.filter(reason=reason_code)
        if reason_consumptions.exists():
            reasons_data[reason_display] = {
                'count': reason_consumptions.count(),
                'items': reason_consumptions
            }
    
    return render(request, 'inventory/report_consumptions.html', {
        'reasons_data': reasons_data,
        'start_date': start_date,
        'end_date': end_date,
        'date_generated': timezone.now()
    })
            