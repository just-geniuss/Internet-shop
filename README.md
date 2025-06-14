# Интернет-магазин автозапчастей с интеграцией 1С

Проект интернет-магазина автозапчастей на базе Django с полноценной интеграцией с системой 1С. 
Позволяет синхронизировать каталог товаров, информацию о заказах и пользователях с учетной системой 1С.

## Основные возможности

- Каталог автозапчастей с категориями и фильтрами
- Поиск по каталогу
- Корзина покупок и оформление заказов
- Личный кабинет пользователя
- История заказов
- Двусторонняя интеграция с 1С
- Административный интерфейс для управления магазином

## Технические требования

- Python 3.10+
- Django 5.1+
- PostgreSQL 14+
- 1С Предприятие (для интеграции)

## Быстрая установка (рекомендуется)

### Автоматическая установка с помощью setup.sh

Самый простой способ настроить и запустить интернет-магазин:

```bash
git clone <repository-url>
cd Internet-shop
./setup.sh
```

Скрипт автоматически:
- Выберет язык интерфейса (русский/английский)
- Запросит режим работы (разработка/продакшн)
- Настроит базу данных PostgreSQL
- Сгенерирует SECRET_KEY и создаст .env файл
- Настроит email и интеграцию с 1С (опционально)
- Создаст nginx конфигурацию для продакшн режима
- Запустит Docker контейнеры
- Выполнит миграции базы данных
- Предложит создать суперпользователя
- Загрузит демонстрационные данные

**Доступ к приложению:**
- **Режим разработки**: http://127.0.0.1:8899
- **Продакшн с Nginx**: http://127.0.0.1:8443
- **Админ панель**: добавьте `/admin/` к любому из адресов выше

## Ручная установка

### Запуск через Docker

#### Режим разработки

#### Режим разработки

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd Internet-shop
```

2. Создать `.env` файл на основе `.env.example`:
```bash
cp .env.example .env
# Отредактируйте .env файл под ваши настройки
```

3. Запустить приложение:
```bash
docker-compose up --build
```

#### Продакшн режим

1. Создать `.env` файл для продакшна:
```bash
cp .env.example .env
```

2. Отредактировать `.env` файл:
```bash
# Установить DEBUG=False
DEBUG=False
# Настроить домен
DOMAIN=yourdomain.com
# Установить надежный SECRET_KEY
SECRET_KEY=your-very-secure-secret-key
# Настроить базу данных
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
```

3. Создать nginx.conf (опционально):
```bash
# Nginx будет перенаправлять с 127.0.0.1:8443 на контейнеры
# См. пример конфигурации в docker-compose.prod.yml
```

4. Запустить продакшн версию:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

5. Создать суперпользователя:
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Остановка контейнеров
```bash
docker-compose down
```

### Запуск в фоновом режиме
```bash
docker-compose up -d
```

### Просмотр логов
```bash
docker-compose logs -f web
```

## Возможные проблемы и решения

### Docker

**Проблема:** Контейнер не может подключиться к базе данных
**Решение:** Убедитесь, что контейнер PostgreSQL полностью запустился перед веб-приложением:
```bash
docker-compose up db
# Дождитесь сообщения "database system is ready to accept connections"
# В другом терминале:
docker-compose up web
```

**Проблема:** Ошибка разрешений при создании файлов
**Решение:** Проверьте права доступа к папкам media и static:
```bash
sudo chown -R $USER:$USER media static logs
chmod -R 755 media static logs
```

**Проблема:** Порт 8899 или 8443 уже занят
**Решение:** Измените порт в docker-compose.yml или остановите процесс, использующий порт:
```bash
# Найти процесс
lsof -i :8899  # для разработки
lsof -i :8443  # для продакшна
# Остановить процесс (замените PID на реальный)
kill PID
```

**Проблема:** Ошибка `ImportError: failed to find libmagic`
**Решение:** Эта ошибка возникает если в системе отсутствует библиотека libmagic. В Dockerfile уже добавлена установка libmagic1, поэтому пересоберите контейнеры:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Проблема:** Контейнеры не запускаются или падают при старте
**Решение:** Проверьте логи контейнеров:
```bash
docker-compose logs web
docker-compose logs db
```

### База данных

**Проблема:** Ошибки миграций
**Решение:** Сбросьте миграции и примените заново:
```bash
docker-compose exec web python manage.py migrate --fake-initial
```

**Проблема:** Нужно сбросить базу данных
**Решение:**
```bash
docker-compose down
docker volume rm internet-shop_postgres_data
docker-compose up --build
```

## Конфигурация для продакшена

Для развертывания в продакшене создайте файл `docker-compose.prod.yml`:

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    container_name: postgres-db-prod
    environment:
      POSTGRES_DB: autoparts_shop
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  web:
    build: .
    container_name: Internet-shop-prod
    command: sh -c "chmod +x entrypoint.sh && ./entrypoint.sh && gunicorn DjangoProject.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=0
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/autoparts_shop
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: always

  nginx:
    image: nginx:alpine
    container_name: nginx-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

Создайте файл `.env` с переменными окружения:
```
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_django_secret_key
```

## Настройка интеграции с 1С

Для настройки интеграции с 1С необходимо:

1. Войти в административную панель Django (`/admin/`)
2. Перейти в раздел "Настройки интеграции с 1С"
3. Добавить настройки подключения к 1С:
   - Строка подключения
   - Имя пользователя
   - Пароль

## Управление настройками (.env файлы)

### Структура .env файла

Приложение использует переменные окружения для настройки. Основные параметры:

```bash
# Режим работы
DEBUG=True  # True для разработки, False для продакшна

# Безопасность
SECRET_KEY=your-secret-key  # Автоматически генерируется setup.sh
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,yourdomain.com
DOMAIN=yourdomain.com

# База данных
DB_ENGINE=django.db.backends.postgresql
DB_NAME=autoparts_shop
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

# Email (опционально)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Интеграция с 1С (опционально)
INTEGRATION_1C_TOKEN=your-secure-token
```

### Создание .env файла вручную

1. Скопируйте пример:
```bash
cp .env.example .env
```

2. Сгенерируйте SECRET_KEY:
```bash
python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
print('SECRET_KEY=' + secret_key)
"
```

3. Отредактируйте остальные параметры в .env файле

### Различия между режимами

| Параметр | Разработка | Продакшн |
|----------|------------|----------|
| DEBUG | True | False |
| ALLOWED_HOSTS | localhost,127.0.0.1 | yourdomain.com |
| SECURE_SSL_REDIRECT | False | True |
| SESSION_COOKIE_SECURE | False | True |
| CSRF_COOKIE_SECURE | False | True |
| Порт доступа | 8899 | 8899 (+ nginx на 8443) |

## Структура проекта

- `catalog/` - приложение каталога товаров
- `orders/` - приложение для работы с заказами
- `users/` - приложение для работы с пользователями
- `integration_1c/` - приложение для интеграции с 1С
- `static/` - статические файлы (CSS, JS, изображения)
- `media/` - загружаемые пользователями файлы
- `templates/` - HTML-шаблоны

## Полезные команды

### Управление контейнерами

```bash
# Запуск в режиме разработки
docker-compose up -d

# Запуск в продакшн режиме
docker-compose -f docker-compose.prod.yml up -d

# Остановка контейнеров
docker-compose down
docker-compose -f docker-compose.prod.yml down

# Перезапуск веб-сервиса
docker-compose restart web
docker-compose -f docker-compose.prod.yml restart web

# Просмотр логов
docker-compose logs -f web
docker-compose -f docker-compose.prod.yml logs -f web

# Выполнение команд внутри контейнера
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Работа с данными

```bash
# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Загрузка демо данных
docker-compose exec web python manage.py loaddata fixtures/categories.json

# Создание дампа данных
docker-compose exec web python manage.py dumpdata > backup.json

# Сборка статических файлов
docker-compose exec web python manage.py collectstatic --noinput
```

### Администрирование

```bash
# Подключение к базе данных
docker-compose exec db psql -U postgres -d autoparts_shop

# Очистка Docker системы
docker system prune -a

# Просмотр запущенных контейнеров
docker-compose ps

# Обновление контейнеров
docker-compose pull
docker-compose up --build -d
```

## Лицензия

Данный проект распространяется под лицензией MIT