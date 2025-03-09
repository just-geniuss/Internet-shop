from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Модель категории автозапчастей"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                               related_name='children', verbose_name='Родительская категория')
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.id])


class Manufacturer(models.Model):
    """Модель производителя автозапчастей"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    logo = models.ImageField('Логотип', upload_to='manufacturers/', blank=True)
    country = models.CharField('Страна', max_length=50, blank=True)
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Car(models.Model):
    """Модель автомобиля"""
    brand = models.CharField('Марка', max_length=50)
    model = models.CharField('Модель', max_length=50)
    year_start = models.PositiveIntegerField('Год начала выпуска')
    year_end = models.PositiveIntegerField('Год окончания выпуска', null=True, blank=True)
    engine_type = models.CharField('Тип двигателя', max_length=50, blank=True)
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['brand', 'model']
    
    def __str__(self):
        return f"{self.brand} {self.model} ({self.year_start}-{self.year_end or 'н.в.'})"


class Product(models.Model):
    """Модель автозапчасти"""
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                related_name='products', verbose_name='Категория')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, 
                                    related_name='products', verbose_name='Производитель')
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField('Остаток на складе', default=0)
    available = models.BooleanField('Доступен', default=True)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True)
    compatible_cars = models.ManyToManyField(Car, blank=True, verbose_name='Совместимые автомобили')
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku', 'external_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.id])


class ProductImage(models.Model):
    """Модель дополнительных изображений автозапчасти"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images', verbose_name='Товар')
    image = models.ImageField('Изображение', upload_to='products/additional/')
    alt = models.CharField('Альтернативный текст', max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
    
    def __str__(self):
        return f"Изображение для {self.product.name}"


class ProductAttribute(models.Model):
    """Модель атрибута автозапчасти"""
    name = models.CharField('Название', max_length=100)
    
    class Meta:
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'
    
    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Модель значения атрибута автозапчасти"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                              related_name='attribute_values', verbose_name='Товар')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, 
                                verbose_name='Атрибут')
    value = models.CharField('Значение', max_length=255)
    
    class Meta:
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибутов'
        unique_together = ('product', 'attribute')
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
