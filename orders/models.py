from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )
    
    PAYMENT_CHOICES = (
        ('cash', 'Наличными при получении'),
        ('card', 'Картой при получении'),
        ('online', 'Онлайн оплата'),
    )
    
    CLIENT_TYPE_CHOICES = (
        ('individual', 'Физическое лицо'),
        ('business', 'Юридическое лицо'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='orders', verbose_name='Пользователь')
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    address = models.CharField('Адрес', max_length=250)
    city = models.CharField('Город', max_length=100)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES)
    payment_completed = models.BooleanField('Оплачено', default=False)
    note = models.TextField('Примечание', blank=True)
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    # Новые поля для разделения типов клиентов
    client_type = models.CharField('Тип клиента', max_length=20, choices=CLIENT_TYPE_CHOICES, default='individual')
    company_name = models.CharField('Название компании', max_length=100, blank=True)
    inn = models.CharField('ИНН', max_length=12, blank=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']
    
    def __str__(self):
        return f'Заказ {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """Модель товара в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                             related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='order_items', verbose_name='Товар')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1, 
                                        validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
    
    def __str__(self):
        return f'{self.product.name} в заказе {self.order.id}'
    
    def get_cost(self):
        return self.price * self.quantity


class Cart(models.Model):
    """Модель корзины"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                             related_name='cart', verbose_name='Пользователь', null=True, blank=True)
    session_key = models.CharField('Ключ сессии', max_length=255, null=True, blank=True)
    created = models.DateTimeField('Создана', auto_now_add=True)
    updated = models.DateTimeField('Обновлена', auto_now=True)
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
    
    def __str__(self):
        return f'Корзина {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class CartItem(models.Model):
    """Модель товара в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, 
                           related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                              verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1, 
                                        validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f'{self.product.name} в корзине {self.cart.id}'
    
    def get_cost(self):
        return self.product.price * self.quantity
