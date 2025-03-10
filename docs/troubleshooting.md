# Устранение распространенных ошибок

## Ошибка импорта `validate_file_extension` из django.core.validators

```
ImportError: cannot import name 'validate_file_extension' from 'django.core.validators'
```

### Решение:

Эта ошибка происходит потому, что валидаторы `validate_file_extension` и `validate_file_size` находятся в нашем собственном модуле, а не в стандартной библиотеке Django.

1. Проверьте импорты в файле `catalog/models.py`, они должны быть:
   ```python
   from DjangoProject.validators import validate_file_extension, validate_file_size
   ```

2. Если у вас возникают проблемы с python-magic, можно использовать альтернативные валидаторы из `DjangoProject.validators_alt`:
   ```python
   from DjangoProject.validators_alt import validate_file_extension, validate_file_size
   ```

## Ошибка при установке python-magic

```
Error: No module named 'magic'
```

### Решение:

#### На Linux (Debian/Ubuntu):
```bash
sudo apt-get update
sudo apt-get install libmagic1
pip install python-magic
```

#### На macOS:
```bash
brew install libmagic
pip install python-magic
```

#### На Windows:
Следуйте инструкциям на странице: https://github.com/ahupp/python-magic#windows

## Проблемы с медиа-файлами и статическими файлами

### Решение:

1. Убедитесь, что каталоги `media` и `static` существуют:
   ```bash
   mkdir -p media static
   ```

2. Проверьте права доступа:
   ```bash
   chmod 755 media static
   ```

3. Убедитесь, что переменные `MEDIA_URL` и `STATIC_URL` правильно настроены в `settings.py`.

4. В режиме разработки проверьте, что в `urls.py` есть строки для обслуживания медиа-файлов:
   ```python
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
       urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   ```

## Ошибки миграции базы данных

### Решение:

1. Попробуйте сначала сделать конкретную миграцию приложения:
   ```bash
   python manage.py migrate catalog
   python manage.py migrate orders
   python manage.py migrate users
   python manage.py migrate integration_1c
   ```

2. Если проблемы продолжаются, можно попробовать сбросить миграции (только для разработки, не для продакшена):
   ```bash
   # Удалите файл базы данных (резервное копирование!)
   rm db.sqlite3
   
   # Создайте миграции заново
   python manage.py makemigrations
   python manage.py migrate
   ```

## Ошибки модуля DjangoProject.validators

Если вы получаете ошибки с модулем DjangoProject.validators, особенно после клонирования:

### Решение:

1. Убедитесь, что файл `DjangoProject/validators.py` существует и содержит все необходимые функции.

2. Попробуйте использовать альтернативные валидаторы, которые не зависят от python-magic:
   ```python
   # В catalog/models.py изменить импорт на:
   from DjangoProject.validators_alt import validate_file_extension, validate_file_size
   ```

## Ошибки с SECRET_KEY

### Решение:

1. Убедитесь, что у вас есть файл `.env` с действительным SECRET_KEY.

2. Если вы используете файл `.env`, убедитесь, что он загружается в `settings.py`:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-for-development')
   ```

## Проблемы с интернационализацией и переводами

### Решение:

1. Убедитесь, что LANGUAGE_CODE установлен правильно в settings.py:
   ```python
   LANGUAGE_CODE = 'ru-ru'
   ```

2. Проверьте настройки часового пояса:
   ```python
   TIME_ZONE = 'Europe/Moscow'
   USE_I18N = True
   USE_TZ = True
   ```

## Ошибки импорта при запуске тестов

### Решение:

1. Убедитесь, что каталог тестов правильно настроен:
   ```
   mkdir -p tests
   touch tests/__init__.py
   ```

2. Проверьте, что тесты найдены:
   ```bash
   python manage.py test --list
   ``` 