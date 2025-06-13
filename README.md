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

## Установка и запуск

### Запуск через Docker (рекомендуется)

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd Internet-shop
```

2. Запустить приложение с помощью Docker Compose:
```bash
docker-compose up --build
```

3. Применить миграции (в отдельном терминале):
```bash
docker-compose exec web python manage.py migrate
```

4. Создать суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Загрузить демонстрационные данные (опционально):
```bash
docker-compose exec web python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json fixtures/products.json fixtures/product_attributes.json fixtures/integration_settings.json
```

Приложение будет доступно по адресу: http://localhost:8000

Административная панель: http://localhost:8000/admin/

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

**Проблема:** Порт 8000 уже занят
**Решение:** Измените порт в docker-compose.yml или остановите процесс, использующий порт:
```bash
# Найти процесс
lsof -i :8000
# Остановить процесс (замените PID на реальный)
kill PID
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

## Структура проекта

- `catalog/` - приложение каталога товаров
- `orders/` - приложение для работы с заказами
- `users/` - приложение для работы с пользователями
- `integration_1c/` - приложение для интеграции с 1С
- `static/` - статические файлы (CSS, JS, изображения)
- `media/` - загружаемые пользователями файлы
- `templates/` - HTML-шаблоны

## Лицензия

Данный проект распространяется под лицензией MIT