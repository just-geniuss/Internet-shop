import os
import logging
from io import BytesIO
from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from django.conf import settings

logger = logging.getLogger(__name__)

def optimize_image(image_field, quality=85, max_width=1200, max_height=1200, format='JPEG'):
    """
    Оптимизирует изображение, уменьшая его размер без существенной потери качества.
    
    Args:
        image_field: Поле изображения модели Django
        quality: Качество сжатия (1-100)
        max_width: Максимальная ширина
        max_height: Максимальная высота
        format: Формат сохранения ('JPEG', 'PNG', 'WEBP')
    
    Returns:
        bool: True если оптимизация выполнена успешно, False в противном случае
    """
    if not image_field:
        return False
    
    try:
        # Открываем изображение с помощью PIL
        img = Image.open(image_field)
        
        # Исправление ориентации на основе EXIF-данных
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            
            exif = dict(img._getexif().items())
            
            if exif[orientation] == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif exif[orientation] == 3:
                img = img.rotate(180)
            elif exif[orientation] == 4:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif exif[orientation] == 5:
                img = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(90)
            elif exif[orientation] == 6:
                img = img.rotate(270)
            elif exif[orientation] == 7:
                img = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(270)
            elif exif[orientation] == 8:
                img = img.rotate(90)
        except (AttributeError, KeyError, IndexError):
            # Изображение не содержит EXIF-данных или они некорректны
            pass
        
        # Проверяем, нужно ли изменять размер
        width, height = img.size
        new_width, new_height = width, height
        
        # Изменяем размер, если изображение слишком большое
        if width > max_width or height > max_height:
            if width > height:
                new_width = max_width
                new_height = int((new_width / width) * height)
            else:
                new_height = max_height
                new_width = int((new_height / height) * width)
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
        # Конвертируем в RGB если нужно (для JPEG)
        if format == 'JPEG' and img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Сохраняем в буфер
        output = BytesIO()
        
        # Определяем формат файла для сохранения
        save_format = format
        if format == 'WEBP' and not settings.DEBUG:  # В production используем WebP
            save_format = 'WEBP'
        elif format == 'WEBP':  # Для разработки используем JPEG, так как некоторые браузеры могут не поддерживать WebP
            save_format = 'JPEG'
        
        # Сохраняем с указанным качеством
        img.save(output, format=save_format, quality=quality, optimize=True)
        output.seek(0)
        
        # Заменяем содержимое поля
        image_name = os.path.basename(image_field.name)
        # Изменяем расширение файла, если нужно
        if save_format != format:
            name_parts = image_name.rsplit('.', 1)
            if len(name_parts) > 1:
                image_name = f"{name_parts[0]}.{save_format.lower()}"
        
        # Сохраняем оптимизированное изображение
        image_field.save(image_name, ContentFile(output.read()), save=False)
        
        logger.info(f"Изображение оптимизировано: {image_name} - {new_width}x{new_height}, формат: {save_format}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при оптимизации изображения: {e}")
        return False

def generate_image_srcset(image_url, widths=[320, 640, 960, 1280]):
    """
    Генерирует наборы разных размеров изображений для тега srcset
    
    Args:
        image_url: URL изображения
        widths: Список ширин для генерации вариантов
    
    Returns:
        str: Строка с атрибутом srcset
    """
    if not image_url:
        return ""
    
    # Разбиваем URL на основной путь и расширение
    base_url, ext = os.path.splitext(image_url)
    
    # Генерируем варианты
    srcset_items = []
    for width in widths:
        srcset_items.append(f"{base_url}-{width}w{ext} {width}w")
    
    return ", ".join(srcset_items) 