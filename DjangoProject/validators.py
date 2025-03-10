import os
import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_extension(value):
    """
    Проверяет расширение загружаемого файла на соответствие разрешенным типам.
    """
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            _('Неподдерживаемый тип файла. Разрешенные типы: %(valid_extensions)s'),
            params={'valid_extensions': ', '.join(valid_extensions)}
        )


def validate_file_size(value):
    """
    Ограничивает размер загружаемого файла.
    """
    # 5MB = 5 * 1024 * 1024
    max_size = 5 * 1024 * 1024
    
    if value.size > max_size:
        raise ValidationError(_('Файл слишком большой. Максимальный размер: 5 МБ.'))


def validate_file_content_type(value):
    """
    Проверяет тип содержимого файла (MIME-тип) для защиты от загрузки вредоносных файлов.
    Требует установки python-magic: pip install python-magic
    """
    # Для корректной работы требуется правильно установленный libmagic
    # На Windows может потребоваться дополнительная настройка
    
    try:
        file_mime = magic.from_buffer(value.read(1024), mime=True)
        value.seek(0)  # Сбрасываем указатель файла в начало
        
        # Разрешенные MIME-типы
        allowed_mime_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
            'application/pdf',
            'application/msword',  # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/vnd.ms-excel',  # .xls
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        ]
        
        if file_mime not in allowed_mime_types:
            raise ValidationError(
                _('Недопустимый тип содержимого файла. Разрешены только изображения (JPEG, PNG, GIF, SVG), PDF, DOC, DOCX, XLS и XLSX.')
            )
    
    except Exception as e:
        raise ValidationError(_('Не удалось проверить тип файла: %(error)s'), params={'error': str(e)})


# Валидатор для проверки SVG файлов на наличие вредоносного кода
def validate_svg_file(value):
    """
    Проверяет SVG-файл на наличие потенциально опасных элементов.
    """
    if not value.name.lower().endswith('.svg'):
        return
    
    # Перемещаем указатель в начало файла
    value.seek(0)
    content = value.read().decode('utf-8')
    
    # Список потенциально опасных элементов/атрибутов в SVG
    dangerous_elements = [
        '<script', 'javascript:', 'onload=', 'onerror=', 'onclick=',
        'onmouseover=', 'eval(', 'data:text/html', 'data:text/javascript',
        '<iframe', '<object', '<embed'
    ]
    
    for element in dangerous_elements:
        if element.lower() in content.lower():
            raise ValidationError(
                _('SVG файл содержит потенциально опасный код. Пожалуйста, проверьте файл.')
            ) 