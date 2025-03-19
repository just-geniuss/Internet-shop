import os
from django.core.management.base import BaseCommand
from django.contrib.sitemaps import ping_google
from django.urls import reverse
from django.conf import settings
from catalog.models import Product, Category
from django.utils import timezone
import xml.dom.minidom
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Генерирует sitemap.xml файл и отправляет его в поисковые системы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ping',
            action='store_true',
            help='Отправить уведомление о обновлении Sitemap в поисковые системы',
        )

    def handle(self, *args, **options):
        try:
            sitemap_path = os.path.join(settings.STATIC_ROOT, 'sitemap.xml')
            os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)
            
            # Создаем XML документ
            doc = xml.dom.minidom.getDOMImplementation().createDocument(
                None, "urlset", None
            )
            root = doc.documentElement
            root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
            
            # Хост
            protocol = 'https' if not settings.DEBUG else 'http'
            host = f"{protocol}://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'example.com'}"
            
            # Добавляем главную страницу
            self._add_url(doc, root, {
                'loc': f"{host}{reverse('catalog:index')}",
                'lastmod': timezone.now().strftime('%Y-%m-%d'),
                'changefreq': 'daily',
                'priority': '1.0'
            })
            
            # Добавляем страницу категорий
            self._add_url(doc, root, {
                'loc': f"{host}{reverse('catalog:categories')}",
                'lastmod': timezone.now().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.8'
            })
            
            # Добавляем все категории
            categories = Category.objects.all()
            self.stdout.write(f"Добавление {categories.count()} категорий в sitemap...")
            for category in categories:
                lastmod = timezone.now()
                # Находим последний обновленный товар в категории
                latest_product = Product.objects.filter(
                    category=category, 
                    available=True,
                    is_visible=True
                ).order_by('-updated').first()
                
                if latest_product:
                    lastmod = latest_product.updated
                
                self._add_url(doc, root, {
                    'loc': f"{host}{category.get_absolute_url()}",
                    'lastmod': lastmod.strftime('%Y-%m-%d'),
                    'changefreq': 'weekly',
                    'priority': '0.7'
                })
            
            # Добавляем все товары
            products = Product.objects.filter(available=True, is_visible=True)
            self.stdout.write(f"Добавление {products.count()} товаров в sitemap...")
            for product in products:
                self._add_url(doc, root, {
                    'loc': f"{host}{product.get_absolute_url()}",
                    'lastmod': product.updated.strftime('%Y-%m-%d'),
                    'changefreq': 'weekly',
                    'priority': '0.6'
                })
            
            # Сохраняем XML файл
            with open(sitemap_path, 'w', encoding='utf-8') as f:
                f.write(doc.toprettyxml(indent="  "))
            
            self.stdout.write(self.style.SUCCESS(f'Sitemap.xml успешно создан: {sitemap_path}'))
            
            # Отправляем пинг в поисковые системы
            if options['ping']:
                try:
                    ping_google('/sitemap.xml')
                    self.stdout.write(self.style.SUCCESS('Уведомление отправлено в Google'))
                    # Здесь можно добавить уведомления для других поисковых систем
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка при отправке уведомления: {e}'))
        
        except Exception as e:
            logger.error(f"Ошибка при генерации sitemap.xml: {e}")
            self.stdout.write(self.style.ERROR(f'Ошибка при генерации sitemap.xml: {e}'))
    
    def _add_url(self, doc, root, url_data):
        """Добавляет URL-узел в корневой элемент"""
        url_node = doc.createElement('url')
        
        # Добавляем location
        loc = doc.createElement('loc')
        loc_text = doc.createTextNode(url_data['loc'])
        loc.appendChild(loc_text)
        url_node.appendChild(loc)
        
        # Добавляем lastmod, если есть
        if 'lastmod' in url_data:
            lastmod = doc.createElement('lastmod')
            lastmod_text = doc.createTextNode(url_data['lastmod'])
            lastmod.appendChild(lastmod_text)
            url_node.appendChild(lastmod)
        
        # Добавляем changefreq, если есть
        if 'changefreq' in url_data:
            changefreq = doc.createElement('changefreq')
            changefreq_text = doc.createTextNode(url_data['changefreq'])
            changefreq.appendChild(changefreq_text)
            url_node.appendChild(changefreq)
        
        # Добавляем priority, если есть
        if 'priority' in url_data:
            priority = doc.createElement('priority')
            priority_text = doc.createTextNode(url_data['priority'])
            priority.appendChild(priority_text)
            url_node.appendChild(priority)
        
        # Добавляем URL в корневой элемент
        root.appendChild(url_node) 