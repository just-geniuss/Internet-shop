# Устранение неполадок

## Часто встречающиеся проблемы

### 1. Ошибка ImportError: failed to find libmagic

**Описание:** При запуске Django возникает ошибка импорта библиотеки libmagic.

**Причина:** В контейнере отсутствует системная библиотека libmagic, необходимая для работы пакета python-magic.

**Решение:**
```bash
# Остановить контейнеры
docker-compose down

# Пересобрать контейнеры без использования кеша
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

### 2. Контейнеры не запускаются

**Симптомы:** 
- Контейнеры падают сразу после запуска
- Сообщения об ошибках в логах

**Диагностика:**
```bash
# Проверить статус контейнеров
docker-compose ps

# Посмотреть логи веб-приложения
docker-compose logs web

# Посмотреть логи базы данных
docker-compose logs db
```

**Возможные решения:**
- Проверить правильность .env файла
- Убедиться что Docker имеет достаточно ресурсов
- Проверить что порты не заняты другими процессами

### 3. Проблемы с базой данных

**Ошибка подключения к PostgreSQL:**
```bash
# Убедиться что контейнер БД запущен
docker-compose ps db

# Проверить логи БД
docker-compose logs db

# Перезапустить БД
docker-compose restart db
```

**Ошибки миграций:**
```bash
# Сбросить миграции
docker-compose exec web python manage.py migrate --fake-initial

# Или полностью пересоздать БД
docker-compose down
docker volume rm internet-shop_postgres_data
docker-compose up -d
```

### 4. Проблемы с портами

**Порт уже занят:**
```bash
# Найти процесс, использующий порт
lsof -i :8899  # для разработки
lsof -i :8443  # для продакшна

# Остановить процесс
kill -9 PID

# Или изменить порт в docker-compose.yml
```

### 5. Проблемы с правами доступа

**Ошибки при создании файлов:**
```bash
# Исправить права на директории
sudo chown -R $USER:$USER media static logs
chmod -R 755 media static logs
```

### 6. Проблемы с setup.sh

**Скрипт не запускается:**
```bash
# Сделать скрипт исполняемым
chmod +x setup.sh

# Запустить с bash
bash setup.sh
```

**Ошибка генерации SECRET_KEY:**
```bash
# Убедиться что установлен Python 3
python3 --version

# Или сгенерировать вручную
openssl rand -base64 32
```

## Полезные команды для диагностики

### Docker
```bash
# Просмотр всех контейнеров
docker ps -a

# Очистка системы Docker
docker system prune -a

# Удаление всех volume
docker volume prune

# Просмотр использования ресурсов
docker stats
```

### Django
```bash
# Проверка настроек Django
docker-compose exec web python manage.py check

# Проверка настроек для продакшна
docker-compose exec web python manage.py check --deploy

# Интерактивная оболочка Django
docker-compose exec web python manage.py shell

# Запуск тестов
docker-compose exec web python manage.py test
```

### База данных
```bash
# Подключение к PostgreSQL
docker-compose exec db psql -U postgres -d autoparts_shop

# Список таблиц
\dt

# Выход из PostgreSQL
\q
```

## Логи и отладка

### Расположение логов
- Django логи: `logs/django.log`
- Логи интеграции с 1С: `logs/integration_1c.log`
- Docker логи: `docker-compose logs [service_name]`

### Включение DEBUG режима
В .env файле:
```
DEBUG=True
```

Затем перезапустить контейнеры:
```bash
docker-compose restart web
```

## Получение помощи

Если проблема не решается:

1. Проверьте документацию Django
2. Посмотрите issue в репозитории проекта
3. Убедитесь что используете последнюю версию
4. Приложите полные логи ошибок при обращении за помощью
