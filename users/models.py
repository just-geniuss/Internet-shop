from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Модель профиля пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.CharField('Адрес', max_length=250, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    postal_code = models.CharField('Почтовый индекс', max_length=20, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    date_of_birth = models.DateField('Дата рождения', blank=True, null=True)
    external_id = models.CharField('Внешний ID (1C)', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f'Профиль пользователя {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании пользователя"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль пользователя при обновлении пользователя"""
    instance.profile.save()
