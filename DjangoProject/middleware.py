from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponse
import time


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления дополнительных заголовков безопасности к HTTP-ответам.
    """
    
    def process_response(self, request, response):
        # Content Security Policy (CSP)
        # Ограничивает источники содержимого, которые может загружать браузер
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https://via.placeholder.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        
        # X-Content-Type-Options
        # Предотвращает MIME-сниффинг браузерами
        response["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        # Активирует встроенную в браузеры защиту от XSS
        response["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        # Контролирует, сколько реферальной информации отправляется
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (бывший Feature-Policy)
        # Ограничивает доступ к различным API браузера
        response["Permissions-Policy"] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "accelerometer=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "payment=()"
        )
        
        return response


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    Middleware для дополнительной защиты от XSS-атак путем фильтрации входящих параметров.
    """
    
    def process_request(self, request):
        # Проверяем GET и POST параметры на наличие подозрительных шаблонов
        for key, value in request.GET.items():
            request.GET = self._sanitize_data(request.GET, key, value)
        
        if request.method == 'POST':
            for key, value in request.POST.items():
                request.POST = self._sanitize_data(request.POST, key, value)
        
        return None
    
    def _sanitize_data(self, data_dict, key, value):
        """
        Очищает потенциально опасные входные данные.
        Обратите внимание, что это базовая защита, и Django уже имеет встроенную защиту от XSS.
        """
        if isinstance(value, str):
            # Список опасных шаблонов
            dangerous_patterns = ['<script', 'javascript:', 'data:text/html', 'onerror=', 'onload=']
            
            # Проверяем каждый опасный шаблон
            for pattern in dangerous_patterns:
                if pattern.lower() in value.lower():
                    # Заменяем опасный контент или устанавливаем пустое значение
                    data_dict = data_dict.copy()
                    data_dict[key] = ''
                    break
                    
        return data_dict


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware для ограничения количества запросов от одного IP-адреса за определенный период времени.
    Защищает от DoS и brute force атак.
    """
    
    def process_request(self, request):
        # Получаем IP-адрес
        ip = self.get_client_ip(request)
        
        # Игнорируем локальные и тестовые адреса
        if ip in ['127.0.0.1', 'localhost']:
            return None
        
        # Получаем текущее время
        now = time.time()
        
        # Ключ для хранения временных меток запросов
        key = f'rate_limit_{ip}'
        
        # Максимальное количество запросов за период
        max_requests = 100
        # Период в секундах (60 секунд = 1 минута)
        period = 60
        
        # Получаем список временных меток предыдущих запросов
        request_times = cache.get(key, [])
        
        # Фильтруем временные метки, оставляя только те, которые попадают в текущий период
        request_times = [t for t in request_times if now - t < period]
        
        # Если количество запросов превышает лимит, возвращаем ошибку 429 (Too Many Requests)
        if len(request_times) >= max_requests:
            response = HttpResponse(
                "Слишком много запросов. Пожалуйста, попробуйте позже.",
                status=429
            )
            response["Retry-After"] = str(period)
            return response
        
        # Добавляем текущую временную метку
        request_times.append(now)
        
        # Сохраняем обновленный список в кеше
        cache.set(key, request_times, period * 2)
        
        return None
    
    def get_client_ip(self, request):
        """
        Метод для получения IP-адреса клиента, учитывая возможные прокси-серверы.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Берем первый IP из списка (реальный IP клиента)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 