from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json


class SecurityHeadersTest(TestCase):
    """
    Тесты для проверки заголовков безопасности в ответах сервера.
    """
    
    def setUp(self):
        # Создаем тестового клиента
        self.client = Client()
        self.response = self.client.get(reverse('catalog:index'))
    
    def test_xss_protection_header(self):
        """Проверяет наличие заголовка X-XSS-Protection."""
        self.assertEqual(self.response.get('X-XSS-Protection'), '1; mode=block')
    
    def test_content_type_options_header(self):
        """Проверяет наличие заголовка X-Content-Type-Options."""
        self.assertEqual(self.response.get('X-Content-Type-Options'), 'nosniff')
    
    def test_content_security_policy_header(self):
        """Проверяет наличие заголовка Content-Security-Policy."""
        self.assertIsNotNone(self.response.get('Content-Security-Policy'))
    
    def test_referrer_policy_header(self):
        """Проверяет наличие заголовка Referrer-Policy."""
        self.assertEqual(self.response.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
    
    def test_permissions_policy_header(self):
        """Проверяет наличие заголовка Permissions-Policy."""
        self.assertIsNotNone(self.response.get('Permissions-Policy'))


class XSSProtectionTest(TestCase):
    """
    Тесты для проверки защиты от XSS-атак.
    """
    
    def setUp(self):
        self.client = Client()
        self.search_url = reverse('catalog:search')
    
    def test_xss_in_search_query(self):
        """Проверяет, что XSS-код в поисковом запросе не выполняется."""
        xss_payload = '<script>alert("XSS")</script>'
        response = self.client.get(f"{self.search_url}?q={xss_payload}")
        
        # Проверяем, что код ответа 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что XSS-код не отображается в исходном виде в ответе
        self.assertNotContains(response, xss_payload)


class CSRFProtectionTest(TestCase):
    """
    Тесты для проверки защиты от CSRF-атак.
    """
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.login_url = reverse('users:login')
        self.username = 'testuser'
        self.password = 'securepassword123'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password
        )
    
    def test_csrf_token_required(self):
        """Проверяет, что POST-запрос без CSRF-токена отклоняется."""
        response = self.client.post(
            self.login_url,
            {'username': self.username, 'password': self.password}
        )
        
        # Должен вернуть 403 Forbidden, так как CSRF-токен отсутствует
        self.assertEqual(response.status_code, 403)


class SQLInjectionTest(TestCase):
    """
    Тесты для проверки защиты от SQL-инъекций.
    """
    
    def setUp(self):
        self.client = Client()
        self.search_url = reverse('catalog:search')
    
    def test_sql_injection_in_search(self):
        """Проверяет, что SQL-инъекция в поисковом запросе не выполняется."""
        # Примеры SQL-инъекций
        sql_payloads = [
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users --"
        ]
        
        for payload in sql_payloads:
            response = self.client.get(f"{self.search_url}?q={payload}")
            
            # Проверяем, что код ответа 200 (OK)
            self.assertEqual(response.status_code, 200)


class AuthenticationSecurityTest(TestCase):
    """
    Тесты для проверки безопасности аутентификации.
    """
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('users:login')
        self.username = 'testuser'
        self.password = 'securepassword123'
        self.user = User.objects.create_user(
            username=self.username,
            email='test@example.com',
            password=self.password
        )
    
    def test_login_with_invalid_credentials(self):
        """Проверяет, что неправильные учетные данные не позволяют войти."""
        response = self.client.post(
            self.login_url,
            {'username': self.username, 'password': 'wrongpassword'},
            follow=True
        )
        
        # Проверяем, что пользователь не аутентифицирован
        self.assertFalse(response.context['user'].is_authenticated) 