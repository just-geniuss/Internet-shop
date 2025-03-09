from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import logging
from .models import IntegrationSettings, SyncLog, SyncEntity
from catalog.models import Product, Category, Manufacturer
from orders.models import Order

# Настройка логгера
logger = logging.getLogger('integration_1c')


def is_staff_user(user):
    """Проверка является ли пользователь сотрудником"""
    return user.is_staff


@user_passes_test(is_staff_user)
def sync_status(request):
    """Статус синхронизации с 1С"""
    logs = SyncLog.objects.all().order_by('-start_time')[:10]
    settings_obj = IntegrationSettings.objects.first()
    entities = SyncEntity.objects.all()
    
    context = {
        'title': 'Статус синхронизации с 1С',
        'logs': logs,
        'settings': settings_obj,
        'entities': entities,
    }
    return render(request, 'integration_1c/sync_status.html', context)


@csrf_exempt
def import_data(request):
    """Импорт данных из 1С"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    # Проверка авторизации (здесь должна быть проверка ключа доступа или токена)
    auth_token = request.headers.get('Authorization')
    if not auth_token or auth_token != settings.INTEGRATION_1C_TOKEN:
        return JsonResponse({'success': False, 'error': 'Неверный токен авторизации'})
    
    # Создание записи в журнале синхронизации
    sync_log = SyncLog.objects.create(
        sync_type='import',
        status='in_progress'
    )
    
    try:
        # Получение JSON-данных из запроса
        data = json.loads(request.body)
        entity_type = data.get('entity_type')
        
        if entity_type == 'product':
            import_products(data)
        elif entity_type == 'category':
            import_categories(data)
        elif entity_type == 'manufacturer':
            import_manufacturers(data)
        else:
            sync_log.status = 'error'
            sync_log.details = f'Неизвестный тип сущности: {entity_type}'
            sync_log.end_time = timezone.now()
            sync_log.save()
            return JsonResponse({'success': False, 'error': 'Неизвестный тип сущности'})
        
        # Обновление записи в журнале
        sync_log.status = 'success'
        sync_log.details = f'Импорт данных {entity_type} успешно завершен'
        sync_log.end_time = timezone.now()
        sync_log.save()
        
        # Обновление времени последней синхронизации
        settings_obj = IntegrationSettings.objects.first()
        if settings_obj:
            settings_obj.last_sync = timezone.now()
            settings_obj.save()
        
        entity = SyncEntity.objects.filter(entity_type=entity_type).first()
        if entity:
            entity.last_sync = timezone.now()
            entity.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f'Ошибка при импорте данных из 1С: {e}')
        
        # Обновление записи в журнале
        sync_log.status = 'error'
        sync_log.details = f'Ошибка при импорте данных: {str(e)}'
        sync_log.end_time = timezone.now()
        sync_log.save()
        
        return JsonResponse({'success': False, 'error': str(e)})


def import_products(data):
    """Импорт товаров из 1С"""
    products_data = data.get('items', [])
    
    for product_data in products_data:
        external_id = product_data.get('external_id')
        
        # Проверка существования товара
        product = Product.objects.filter(external_id=external_id).first()
        
        # Получение связанных объектов
        category = Category.objects.filter(external_id=product_data.get('category_id')).first()
        manufacturer = Manufacturer.objects.filter(external_id=product_data.get('manufacturer_id')).first()
        
        if not category or not manufacturer:
            logger.warning(f'Не найдена категория или производитель для товара {external_id}')
            continue
        
        if product:
            # Обновление существующего товара
            product.name = product_data.get('name')
            product.sku = product_data.get('sku')
            product.description = product_data.get('description', '')
            product.price = product_data.get('price')
            product.stock = product_data.get('stock', 0)
            product.available = product_data.get('available', True)
            product.category = category
            product.manufacturer = manufacturer
            product.save()
        else:
            # Создание нового товара
            product = Product.objects.create(
                name=product_data.get('name'),
                slug=product_data.get('slug', '').lower() or product_data.get('sku').lower(),
                sku=product_data.get('sku'),
                description=product_data.get('description', ''),
                price=product_data.get('price'),
                stock=product_data.get('stock', 0),
                available=product_data.get('available', True),
                category=category,
                manufacturer=manufacturer,
                external_id=external_id
            )


def import_categories(data):
    """Импорт категорий из 1С"""
    categories_data = data.get('items', [])
    
    for category_data in categories_data:
        external_id = category_data.get('external_id')
        
        # Проверка существования категории
        category = Category.objects.filter(external_id=external_id).first()
        
        # Получение родительской категории, если указана
        parent = None
        parent_id = category_data.get('parent_id')
        if parent_id:
            parent = Category.objects.filter(external_id=parent_id).first()
        
        if category:
            # Обновление существующей категории
            category.name = category_data.get('name')
            category.description = category_data.get('description', '')
            category.parent = parent
            category.save()
        else:
            # Создание новой категории
            category = Category.objects.create(
                name=category_data.get('name'),
                slug=category_data.get('slug', '').lower() or category_data.get('name').lower().replace(' ', '-'),
                description=category_data.get('description', ''),
                parent=parent,
                external_id=external_id
            )


def import_manufacturers(data):
    """Импорт производителей из 1С"""
    manufacturers_data = data.get('items', [])
    
    for manufacturer_data in manufacturers_data:
        external_id = manufacturer_data.get('external_id')
        
        # Проверка существования производителя
        manufacturer = Manufacturer.objects.filter(external_id=external_id).first()
        
        if manufacturer:
            # Обновление существующего производителя
            manufacturer.name = manufacturer_data.get('name')
            manufacturer.description = manufacturer_data.get('description', '')
            manufacturer.country = manufacturer_data.get('country', '')
            manufacturer.save()
        else:
            # Создание нового производителя
            manufacturer = Manufacturer.objects.create(
                name=manufacturer_data.get('name'),
                slug=manufacturer_data.get('slug', '').lower() or manufacturer_data.get('name').lower().replace(' ', '-'),
                description=manufacturer_data.get('description', ''),
                country=manufacturer_data.get('country', ''),
                external_id=external_id
            )


@csrf_exempt
def export_data(request):
    """Экспорт данных в 1С"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    # Проверка авторизации (здесь должна быть проверка ключа доступа или токена)
    auth_token = request.headers.get('Authorization')
    if not auth_token or auth_token != settings.INTEGRATION_1C_TOKEN:
        return JsonResponse({'success': False, 'error': 'Неверный токен авторизации'})
    
    # Создание записи в журнале синхронизации
    sync_log = SyncLog.objects.create(
        sync_type='export',
        status='in_progress'
    )
    
    try:
        # Получение данных из запроса
        data = json.loads(request.body)
        entity_type = data.get('entity_type')
        last_sync = data.get('last_sync')
        
        if entity_type == 'order':
            result = export_orders(last_sync)
        else:
            sync_log.status = 'error'
            sync_log.details = f'Неизвестный тип сущности для экспорта: {entity_type}'
            sync_log.end_time = timezone.now()
            sync_log.save()
            return JsonResponse({'success': False, 'error': 'Неизвестный тип сущности для экспорта'})
        
        # Обновление записи в журнале
        sync_log.status = 'success'
        sync_log.details = f'Экспорт данных {entity_type} успешно завершен'
        sync_log.end_time = timezone.now()
        sync_log.save()
        
        # Обновление времени последней синхронизации
        entity = SyncEntity.objects.filter(entity_type=entity_type).first()
        if entity:
            entity.last_sync = timezone.now()
            entity.save()
        
        return JsonResponse({'success': True, 'data': result})
        
    except Exception as e:
        logger.error(f'Ошибка при экспорте данных в 1С: {e}')
        
        # Обновление записи в журнале
        sync_log.status = 'error'
        sync_log.details = f'Ошибка при экспорте данных: {str(e)}'
        sync_log.end_time = timezone.now()
        sync_log.save()
        
        return JsonResponse({'success': False, 'error': str(e)})


def export_orders(last_sync=None):
    """Экспорт заказов в 1С"""
    # Фильтрация заказов по дате создания, если указана дата последней синхронизации
    orders_query = Order.objects.all()
    if last_sync:
        orders_query = orders_query.filter(created__gt=last_sync)
    
    orders_data = []
    for order in orders_query:
        order_items = []
        for item in order.items.all():
            order_items.append({
                'product_id': item.product.external_id,
                'quantity': item.quantity,
                'price': float(item.price),
                'total': float(item.get_cost()),
            })
        
        orders_data.append({
            'order_id': order.id,
            'external_id': order.external_id,
            'created': order.created.isoformat(),
            'status': order.status,
            'payment_method': order.payment_method,
            'payment_completed': order.payment_completed,
            'customer': {
                'first_name': order.first_name,
                'last_name': order.last_name,
                'email': order.email,
                'phone': order.phone,
                'address': order.address,
                'city': order.city,
                'postal_code': order.postal_code,
            },
            'items': order_items,
            'total': float(order.get_total_cost()),
        })
    
    return orders_data


@csrf_exempt
def api_products(request):
    """API для работы с товарами"""
    # Получение списка товаров
    if request.method == 'GET':
        products = Product.objects.filter(available=True)
        
        # Фильтрация по категории, если указана
        category_id = request.GET.get('category_id')
        if category_id:
            products = products.filter(category__external_id=category_id)
        
        # Фильтрация по производителю, если указан
        manufacturer_id = request.GET.get('manufacturer_id')
        if manufacturer_id:
            products = products.filter(manufacturer__external_id=manufacturer_id)
        
        # Формирование ответа
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'external_id': product.external_id,
                'name': product.name,
                'sku': product.sku,
                'price': float(product.price),
                'stock': product.stock,
                'available': product.available,
                'category': {
                    'id': product.category.id,
                    'external_id': product.category.external_id,
                    'name': product.category.name,
                },
                'manufacturer': {
                    'id': product.manufacturer.id,
                    'external_id': product.manufacturer.external_id,
                    'name': product.manufacturer.name,
                },
            })
        
        return JsonResponse({'success': True, 'products': products_data})
    
    # Обработка других методов
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})


@csrf_exempt
def api_orders(request):
    """API для работы с заказами"""
    # Получение списка заказов
    if request.method == 'GET':
        orders = Order.objects.all()
        
        # Фильтрация по статусу, если указан
        status = request.GET.get('status')
        if status:
            orders = orders.filter(status=status)
        
        # Формирование ответа
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'external_id': order.external_id,
                'created': order.created.isoformat(),
                'status': order.status,
                'total': float(order.get_total_cost()),
            })
        
        return JsonResponse({'success': True, 'orders': orders_data})
    
    # Обновление статуса заказа
    elif request.method == 'POST':
        # Проверка авторизации
        auth_token = request.headers.get('Authorization')
        if not auth_token or auth_token != settings.INTEGRATION_1C_TOKEN:
            return JsonResponse({'success': False, 'error': 'Неверный токен авторизации'})
        
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            external_id = data.get('external_id')
            status = data.get('status')
            
            # Поиск заказа
            order = None
            if order_id:
                order = Order.objects.filter(id=order_id).first()
            elif external_id:
                order = Order.objects.filter(external_id=external_id).first()
            
            if not order:
                return JsonResponse({'success': False, 'error': 'Заказ не найден'})
            
            # Обновление статуса
            if status:
                order.status = status
            
            # Обновление внешнего ID, если не указан
            if external_id and not order.external_id:
                order.external_id = external_id
            
            order.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f'Ошибка при обновлении заказа: {e}')
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Обработка других методов
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
