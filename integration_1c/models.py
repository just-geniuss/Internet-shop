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
        return f'{self.name} ({self.get_entity_type_display()})'
