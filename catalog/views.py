from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product, Manufacturer


def index(request):
    """Главная страница каталога"""
    categories = Category.objects.filter(parent=None)[:6]
    featured_products = Product.objects.filter(available=True).order_by('-created')[:8]
    
    context = {
        'title': 'Интернет-магазин автозапчастей',
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'catalog/index.html', context)


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
    subcategories = category.children.all()
    products = category.products.filter(available=True)
    
    # Фильтрация
    manufacturers = request.GET.getlist('manufacturer')
    if manufacturers:
        products = products.filter(manufacturer__id__in=manufacturers)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Сортировка
    sort = request.GET.get('sort', 'name')
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    
    all_manufacturers = Manufacturer.objects.filter(products__category=category).distinct()
    
    context = {
        'title': category.name,
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'all_manufacturers': all_manufacturers,
        'selected_manufacturers': manufacturers,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, product_id):
    """Детальная информация о товаре"""
    product = get_object_or_404(Product, id=product_id, available=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
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
        ).filter(available=True)
    
    context = {
        'title': f'Поиск: {query}',
        'query': query,
        'products': products,
    }
    return render(request, 'catalog/search.html', context)
