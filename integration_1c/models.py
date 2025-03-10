from django.db import models

# Create your models here.

class IntegrationSettings(models.Model):
    """Модель настроек интеграции с 1С"""
    connection_string = models.CharField('Строка подключения к 1С', max_length=500)
    username = models.CharField('Имя пользователя', max_length=100)
    password = models.CharField('Пароль', max_length=100)
    enabled = models.BooleanField('Включено', default=True)
    last_sync = models.DateTimeField('Последняя синхронизация', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Настройки интеграции с 1С'
        verbose_name_plural = 'Настройки интеграции с 1С'
    
    def __str__(self):
        return 'Настройки интеграции с 1С'


class SyncLog(models.Model):
    """Модель журнала синхронизации"""
    SYNC_TYPES = (
        ('import', 'Импорт из 1С'),
        ('export', 'Экспорт в 1С'),
    )
    
    SYNC_STATUS = (
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
        ('in_progress', 'В процессе'),
    )
    
    sync_type = models.CharField('Тип синхронизации', max_length=10, choices=SYNC_TYPES)
    status = models.CharField('Статус', max_length=20, choices=SYNC_STATUS)
    start_time = models.DateTimeField('Время начала', auto_now_add=True)
    end_time = models.DateTimeField('Время окончания', null=True, blank=True)
    details = models.TextField('Детали', blank=True)
    
    class Meta:
        verbose_name = 'Журнал синхронизации'
        verbose_name_plural = 'Журнал синхронизации'
        ordering = ['-start_time']
    
    def __str__(self):
        return f'{self.get_sync_type_display()} - {self.start_time}'


class SyncEntity(models.Model):
    """Модель сущности синхронизации"""
    ENTITY_TYPES = (
        ('product', 'Товар'),
        ('category', 'Категория'),
        ('manufacturer', 'Производитель'),
        ('order', 'Заказ'),
        ('user', 'Пользователь'),
    )
    
    name = models.CharField('Название', max_length=100)
    entity_type = models.CharField('Тип сущности', max_length=20, choices=ENTITY_TYPES)
    is_active = models.BooleanField('Активно', default=True)
    last_sync = models.DateTimeField('Последняя синхронизация', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Сущность синхронизации'
        verbose_name_plural = 'Сущности синхронизации'
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"


class ImportSetting(models.Model):
    """Настройки импорта товаров из 1С"""
    DEFAULT_VISIBILITY = (
        ('visible', 'Показывать на сайте'),
        ('hidden', 'Скрывать с сайта'),
        ('prompt', 'Спрашивать при импорте'),
    )
    
    default_category = models.ForeignKey('catalog.Category', 
                                        on_delete=models.SET_NULL, 
                                        null=True, blank=True,
                                        verbose_name='Категория по умолчанию',
                                        help_text='Если категория товара не найдена, будет использована эта')
    
    default_visibility = models.CharField('Видимость товаров по умолчанию', 
                                         max_length=10, 
                                         choices=DEFAULT_VISIBILITY,
                                         default='prompt',
                                         help_text='Видимость новых товаров на сайте при импорте')
    
    allow_price_edit = models.BooleanField('Разрешить редактирование цены', 
                                          default=True,
                                          help_text='Позволяет указать цену товара при импорте')
    
    allow_category_edit = models.BooleanField('Разрешить выбор категории', 
                                             default=True,
                                             help_text='Позволяет выбрать категорию товара при импорте')
    
    class Meta:
        verbose_name = 'Настройки импорта'
        verbose_name_plural = 'Настройки импорта'
    
    def __str__(self):
        return 'Настройки импорта товаров'


class PendingImport(models.Model):
    """Модель товаров, ожидающих импорта из 1С"""
    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('imported', 'Импортирован'),
        ('rejected', 'Отклонен'),
    )
    
    external_id = models.CharField('Внешний ID', max_length=100, unique=True)
    data = models.TextField('Данные товара', help_text='Данные товара в формате JSON')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Товар ожидающий импорта'
        verbose_name_plural = 'Товары ожидающие импорта'
        ordering = ['-created']
    
    def __str__(self):
        return f"Товар {self.external_id} ({self.get_status_display()})"
    
    def get_product_name(self):
        """Получить название товара из данных"""
        import json
        try:
            data = json.loads(self.data)
            return data.get('name', 'Товар без названия')
        except:
            return 'Неизвестный товар'
            
    def get_product_data(self):
        """Получить данные товара из JSON"""
        import json
        try:
            return json.loads(self.data)
        except:
            return {'name': 'Неизвестный товар', 'sku': '', 'description': '', 'price': 0, 'stock': 0}
