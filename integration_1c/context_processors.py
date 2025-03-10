from .models import PendingImport

def pending_imports_count(request):
    """
    Добавляет количество товаров, ожидающих импорта, в контекст.
    Используется для отображения числа в меню администратора.
    """
    count = 0
    if request.user.is_authenticated and request.user.is_staff:
        count = PendingImport.objects.filter(status='pending').count()
    
    return {
        'pending_items_count': count
    } 