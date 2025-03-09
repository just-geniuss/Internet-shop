from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from catalog.models import Product
from .models import Cart, CartItem, Order, OrderItem


def get_cart(request):
    """Получение или создание корзины для пользователя/сессии"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart(request):
    """Отображение корзины пользователя"""
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'title': 'Корзина',
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/cart.html', context)


def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        cart_item = cart.items.get(product=product)
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Количество товара "{product.name}" обновлено в корзине.')
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        messages.success(request, f'Товар "{product.name}" добавлен в корзину.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_cost(),
            'cart_items_count': cart.items.count(),
        })
    
    return redirect('orders:cart')


def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    
    # Проверка принадлежности товара корзине пользователя
    cart = get_cart(request)
    if cart_item.cart != cart:
        messages.error(request, 'Ошибка доступа к корзине.')
        return redirect('orders:cart')
    
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_cost(),
            'cart_items_count': cart.items.count(),
        })
    
    return redirect('orders:cart')


@login_required
def checkout(request):
    """Оформление заказа"""
    cart = get_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста.')
        return redirect('orders:cart')
    
    # Предзаполнение данных из профиля пользователя
    initial_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'postal_code': profile.postal_code,
        }
    
    if request.method == 'POST':
        # Здесь будет обработка формы заказа
        # В реальном проекте следует использовать Django Forms
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            postal_code=request.POST.get('postal_code'),
            payment_method=request.POST.get('payment_method'),
            note=request.POST.get('note', '')
        )
        
        # Создание элементов заказа из корзины
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Очистка корзины после оформления заказа
        cart_items.delete()
        
        messages.success(request, f'Заказ №{order.id} успешно оформлен!')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'title': 'Оформление заказа',
        'cart': cart,
        'cart_items': cart_items,
        'initial': initial_data,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_history(request):
    """История заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    context = {
        'title': 'История заказов',
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Детальная информация о заказе"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'title': f'Заказ №{order.id}',
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)
