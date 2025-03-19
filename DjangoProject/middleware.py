from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponse
import time


class SecurityHeadersMiddleware:
    """
    Добавляет заголовки безопасности в HTTP-ответы
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Добавляем заголовки безопасности
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Feature-Policy'] = "geolocation 'self'; microphone 'none'; camera 'none'"
        response['Permissions-Policy'] = "geolocation=(self), microphone=(), camera=()"
        
        return response


class XSSProtectionMiddleware:
    """
    Защита от XSS-атак для входящих данных
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверка входящих POST и GET данных
        if request.method == 'POST':
            self._sanitize_post_data(request)
        
        if request.GET:
            self._sanitize_get_data(request)
            
        return self.get_response(request)
    
    def _sanitize_post_data(self, request):
        """Очистка данных POST-запроса"""
        # Удаляем потенциально опасные символы из POST данных
        for key in request.POST:
            if isinstance(request.POST[key], str):
                request.POST._mutable = True
                request.POST[key] = self._clean_xss(request.POST[key])
                request.POST._mutable = False
    
    def _sanitize_get_data(self, request):
        """Очистка данных GET-запроса"""
        # Удаляем потенциально опасные символы из GET данных
        for key in request.GET:
            if isinstance(request.GET[key], str):
                request.GET._mutable = True
                request.GET[key] = self._clean_xss(request.GET[key])
                request.GET._mutable = False
    
    def _clean_xss(self, value):
        """Очистка строки от потенциальных XSS-атак"""
        # Заменяем потенциально опасные символы
        value = value.replace('<script>', '')
        value = value.replace('</script>', '')
        value = value.replace('javascript:', '')
        value = value.replace('onerror=', '')
        value = value.replace('onload=', '')
        return value


class RateLimitMiddleware:
    """
    Ограничение количества запросов (защита от DDoS)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
        self.max_requests = 100  # Максимальное количество запросов
        self.window_seconds = 60  # Окно в секундах

    def __call__(self, request):
        import time
        
        # Получаем IP-адрес из запроса
        ip = self._get_client_ip(request)
        current_time = int(time.time())
        
        # Инициализация счетчика для IP, если его еще нет
        if ip not in self.requests:
            self.requests[ip] = {'count': 0, 'timestamp': current_time}
        
        # Сброс счетчика, если прошло достаточно времени
        if current_time - self.requests[ip]['timestamp'] > self.window_seconds:
            self.requests[ip] = {'count': 0, 'timestamp': current_time}
        
        # Увеличиваем счетчик запросов
        self.requests[ip]['count'] += 1
        
        # Если превышен лимит запросов
        if self.requests[ip]['count'] > self.max_requests:
            from django.http import HttpResponseTooManyRequests
            return HttpResponseTooManyRequests("Too many requests. Please try again later.")
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """Получаем IP-адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 