from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PendingImport, ImportSetting, SyncLog, SyncEntity, IntegrationSettings
from catalog.models import Category, Manufacturer, Product
import json


class Integration1CTestCase(TestCase):
    """Тесты для модуля интеграции с 1С"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        # Создаем тестового пользователя и администратора
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.staff_user = User.objects.create_user(
            username='staffuser', 
            password='12345', 
            is_staff=True
        )
        
        # Создаем тестовую категорию и производителя
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category',
            external_id='test-category-1'
        )
        
        self.manufacturer = Manufacturer.objects.create(
            name='Тестовый производитель',
            slug='test-manufacturer',
            country='Россия',
            external_id='test-manufacturer-1'
        )
        
        # Создаем тестовый элемент для импорта
        self.pending_import = PendingImport.objects.create(
            external_id='test-product-123',
            data=json.dumps({
                'external_id': 'test-product-123',
                'name': 'Тестовый товар',
                'sku': 'TEST-123',
                'description': 'Описание тестового товара',
                'price': 1000,
                'stock': 10,
                'available': True,
                'manufacturer_id': self.manufacturer.external_id,
                'category_id': self.category.external_id
            }),
            status='pending'
        )
        
        # Создаем тестовые настройки импорта
        self.import_settings = ImportSetting.objects.create(
            default_category=self.category,
            default_visibility='prompt',
            allow_price_edit=True,
            allow_category_edit=True
        )
        
        # Создаем тестовую сущность синхронизации
        self.sync_entity = SyncEntity.objects.create(
            name='Товары',
            entity_type='product',
            is_active=True
        )
        
        # Создаем тестовый клиент
        self.client = Client()
    
    def test_pending_imports_view_requires_staff(self):
        """Проверка доступа к странице отложенных импортов только для сотрудников"""
        # Анонимный пользователь должен быть перенаправлен
        response = self.client.get(reverse('integration_1c:pending_imports'))
        self.assertNotEqual(response.status_code, 200)
        
        # Обычный пользователь должен быть перенаправлен
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('integration_1c:pending_imports'))
        self.assertNotEqual(response.status_code, 200)
        
        # Сотрудник должен получить доступ
        self.client.login(username='staffuser', password='12345')
        response = self.client.get(reverse('integration_1c:pending_imports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'integration_1c/pending_imports.html')
    
    def test_process_pending_import_view(self):
        """Проверка страницы обработки отложенного импорта"""
        self.client.login(username='staffuser', password='12345')
        
        # Проверка GET-запроса (открытие страницы)
        response = self.client.get(
            reverse('integration_1c:process_pending_import', args=[self.pending_import.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'integration_1c/process_pending_import.html')
        
        # Проверяем, что в контексте есть данные товара
        self.assertTrue('product_data' in response.context)
        self.assertEqual(response.context['product_data']['name'], 'Тестовый товар')
    
    def test_edit_pending_import_view(self):
        """Проверка страницы редактирования отложенного импорта"""
        self.client.login(username='staffuser', password='12345')
        
        # Проверка GET-запроса (открытие страницы)
        response = self.client.get(
            reverse('integration_1c:edit_pending_import', args=[self.pending_import.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'integration_1c/edit_pending_import.html')
    
    def test_reject_pending_import_view(self):
        """Проверка возможности отклонения импорта товара"""
        self.client.login(username='staffuser', password='12345')
        
        # Проверка GET-запроса (отклонение импорта)
        response = self.client.get(
            reverse('integration_1c:reject_pending_import', args=[self.pending_import.id])
        )
        
        # Должно быть перенаправление на страницу списка
        self.assertRedirects(response, reverse('integration_1c:pending_imports'))
        
        # Проверяем, что статус изменился на 'rejected'
        self.pending_import.refresh_from_db()
        self.assertEqual(self.pending_import.status, 'rejected')
    
    def test_sync_status_view(self):
        """Проверка страницы статуса синхронизации"""
        self.client.login(username='staffuser', password='12345')
        
        # Создаем тестовый лог синхронизации
        SyncLog.objects.create(
            sync_type='import',
            status='completed',
            details='Тестовая синхронизация'
        )
        
        # Проверка GET-запроса
        response = self.client.get(reverse('integration_1c:sync_status'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'integration_1c/sync_status.html')
        
        # Проверяем, что в контексте есть логи синхронизации
        self.assertTrue('sync_logs' in response.context)
        self.assertEqual(len(response.context['sync_logs']), 1)


class PendingImportModelTest(TestCase):
    """Тесты для модели PendingImport"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.pending_import = PendingImport.objects.create(
            external_id='test-product-123',
            data=json.dumps({
                'external_id': 'test-product-123',
                'name': 'Тестовый товар',
                'sku': 'TEST-123'
            }),
            status='pending'
        )
    
    def test_get_product_name(self):
        """Проверка получения имени товара из JSON-данных"""
        self.assertEqual(self.pending_import.get_product_name(), 'Тестовый товар')
        
        # Проверка с невалидным JSON
        self.pending_import.data = 'invalid json'
        self.assertEqual(self.pending_import.get_product_name(), 'Неизвестный товар')
