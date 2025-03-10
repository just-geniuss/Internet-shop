import os
import imghdr
import mimetypes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_extension(value):
    """
    Проверяет расширение загружаемого файла на соответствие разрешенным типам.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    if not ext in valid_extensions:
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


def validate_image_file(value):
    """
    Проверяет, является ли файл изображением, используя встроенный модуль imghdr вместо python-magic.
    """
    # Перемещаем указатель файла в начало
    value.seek(0)
    
    # Проверяем, является ли файл изображением
    image_type = imghdr.what(None, value.read())
    value.seek(0)  # Сбрасываем указатель в начало
    
    if image_type not in ['jpeg', 'png', 'gif']:
        raise ValidationError(_('Загружаемый файл не является изображением. Допустимые форматы: JPEG, PNG, GIF.'))


def validate_file_mime_type(value):
    """
    Проверяет MIME-тип файла на основе его расширения, используя встроенный модуль mimetypes.
    Менее надежно, чем проверка с python-magic, но не требует дополнительных зависимостей.
    """
    # Определяем тип файла по расширению
    mime_type, encoding = mimetypes.guess_type(value.name)
    
    if mime_type is None:
        raise ValidationError(_('Невозможно определить тип файла.'))
    
    allowed_mime_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml',
        'application/pdf',
        'application/msword',  # .doc
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.ms-excel',  # .xls
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    ]
    
    if mime_type not in allowed_mime_types:
        raise ValidationError(
            _('Недопустимый тип содержимого файла. Разрешены только изображения (JPEG, PNG, GIF, SVG), PDF, DOC, DOCX, XLS и XLSX.')
        )


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