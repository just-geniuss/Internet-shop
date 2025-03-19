from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category, ProductImage
from .utils import optimize_image
import logging

logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=Product)
def invalidate_sitemap_cache_on_product_change(sender, instance, **kwargs):
    """
    Сбрасываем кеш sitemap при изменении товаров
    """
    try:
        # Очищаем кеш для sitemap
        cache_keys = [
            'sitemap_index',
            'sitemap_products',
            'sitemap_categories',
            'sitemap_static',
        ]
        for key in cache_keys:
            cache.delete(key)
        logger.info(f"Sitemap cache invalidated after product change: {instance.name}")
    except Exception as e:
        logger.error(f"Error invalidating sitemap cache: {e}")

@receiver([post_save, post_delete], sender=Category)
def invalidate_sitemap_cache_on_category_change(sender, instance, **kwargs):
    """
    Сбрасываем кеш sitemap при изменении категорий
    """
    try:
        # Очищаем кеш для sitemap
        cache_keys = [
            'sitemap_index',
            'sitemap_categories',
            'sitemap_static',
        ]
        for key in cache_keys:
            cache.delete(key)
        logger.info(f"Sitemap cache invalidated after category change: {instance.name}")
    except Exception as e:
        logger.error(f"Error invalidating sitemap cache: {e}")

@receiver(post_save, sender=Product)
def optimize_product_image(sender, instance, **kwargs):
    """
    Оптимизируем изображения товаров при сохранении
    """
    if instance.image:
        try:
            optimize_image(instance.image, quality=85, max_width=1200, max_height=1200, format='WEBP')
            logger.info(f"Оптимизировано основное изображение для товара {instance.name}")
        except Exception as e:
            logger.error(f"Ошибка при оптимизации изображения товара {instance.name}: {e}")

@receiver(post_save, sender=Category)
def optimize_category_image(sender, instance, **kwargs):
    """
    Оптимизируем изображения категорий при сохранении
    """
    if instance.image:
        try:
            optimize_image(instance.image, quality=85, max_width=800, max_height=800, format='WEBP')
            logger.info(f"Оптимизировано изображение для категории {instance.name}")
        except Exception as e:
            logger.error(f"Ошибка при оптимизации изображения категории {instance.name}: {e}")

@receiver(post_save, sender=ProductImage)
def optimize_product_additional_image(sender, instance, **kwargs):
    """
    Оптимизируем дополнительные изображения товаров при сохранении
    """
    if instance.image:
        try:
            optimize_image(instance.image, quality=85, max_width=1200, max_height=1200, format='WEBP')
            logger.info(f"Оптимизировано дополнительное изображение для товара {instance.product.name}")
        except Exception as e:
            logger.error(f"Ошибка при оптимизации дополнительного изображения: {e}")

@receiver(pre_save, sender=Product)
def generate_product_slug(sender, instance, **kwargs):
    """
    Автоматически генерируем slug для товара, если его нет
    """
    from django.utils.text import slugify
    if not instance.slug:
        slug_base = f"{instance.name}-{instance.sku}"
        instance.slug = slugify(slug_base, allow_unicode=True)
        logger.info(f"Сгенерирован slug для товара: {instance.slug}")

@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    """
    Автоматически генерируем slug для категории, если его нет
    """
    from django.utils.text import slugify
    if not instance.slug:
        instance.slug = slugify(instance.name, allow_unicode=True)
        logger.info(f"Сгенерирован slug для категории: {instance.slug}") 