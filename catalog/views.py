from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product, Manufacturer
from django.http import HttpResponse
from django.conf import settings


def index(request):
    """Главная страница каталога"""
    categories = Category.objects.filter(parent=None)[:6]
    featured_products = Product.objects.filter(available=True, is_visible=True).order_by('-created')[:8]
    
    context = {
        'title': 'Интернет-магазин автозапчастей',
        'categories': categories,
        'products': featured_products,
    }
    return render(request, 'index.html', context)


def categories(request):
    """Список всех категорий"""
    categories = Category.objects.filter(parent=None)
    
    context = {
        'title': 'Категории автозапчастей',
        'categories': categories,
    }
    return render(request, 'catalog/categories.html', context)


def category_detail(request, category_id):
    """Отображение конкретной категории и её товаров"""
    category = get_object_or_404(Category, id=category_id)
    products = category.products.filter(available=True, is_visible=True)
    
    # Фильтрация
    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(manufacturer__id=manufacturer_id)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Сортировка
    sort_by = request.GET.get('sort_by', 'name')
    products = products.order_by(sort_by)
    
    # Получаем всех производителей для фильтра
    manufacturers = Manufacturer.objects.filter(
        products__category=category, 
        products__is_visible=True
    ).distinct()
    
    context = {
        'title': category.name,
        'category': category,
        'products': products,
        'manufacturers': manufacturers,
        'selected_manufacturer': manufacturer_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, product_id):
    """Детальная информация о товаре"""
    product = get_object_or_404(Product, id=product_id, available=True, is_visible=True)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True, 
        is_visible=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'title': product.name,
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)


def search(request):
    """Поиск товаров"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(sku__icontains=query)
        ).filter(available=True, is_visible=True)
    
    context = {
        'title': f'Поиск: {query}',
        'query': query,
        'products': products,
    }
    return render(request, 'catalog/search.html', context)


def robots_txt(request):
    """Динамическая генерация robots.txt в зависимости от среды"""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /orders/checkout/",
        "Disallow: /users/login/",
        "Disallow: /users/register/",
        "Disallow: /users/profile/",
        "Disallow: /integration/",
        "Allow: /",
        "Allow: /catalog/",
        "Allow: /static/",
        "Allow: /media/",
    ]
    
    # Получаем все категории для индексации
    categories = Category.objects.all()
    for category in categories:
        lines.append(f"Allow: {category.get_absolute_url()}")
    
    # Добавляем ссылку на sitemap
    host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    lines.append(f"\nSitemap: {protocol}://{host}/sitemap.xml")
    
    return HttpResponse("\n".join(lines), content_type="text/plain")
