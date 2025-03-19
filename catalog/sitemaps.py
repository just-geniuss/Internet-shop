from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category, Product
from django.utils import timezone


class ProductSitemap(Sitemap):
    """Карта сайта для товаров"""
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return Product.objects.filter(available=True, is_visible=True)
    
    def lastmod(self, obj):
        return obj.updated
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    """Карта сайта для категорий"""
    changefreq = "monthly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return Category.objects.all()
    
    def lastmod(self, obj):
        # Использовать дату последнего обновленного товара в категории
        latest_product = Product.objects.filter(
            category=obj, 
            available=True,
            is_visible=True
        ).order_by('-updated').first()
        
        if latest_product:
            return latest_product.updated
        return timezone.now()
    
    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    """Карта сайта для статических страниц"""
    changefreq = "monthly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return ['catalog:index', 'catalog:categories', 'catalog:search']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        return timezone.now() 