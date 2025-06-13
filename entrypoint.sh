#!/bin/bash

echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do sleep 1; done

echo "PostgreSQL is up - БД запущена"

# Создаем необходимые директории
mkdir -p media static logs
chmod 755 media static
touch logs/django.log

# Применяем миграции
echo "Applying migrations - Применяем миграции"
python manage.py makemigrations
python manage.py migrate

echo "Migrations applied - Миграции применены"

# Собираем статические файлы
echo "Collecting static files - Собираем статические файлы"
python manage.py collectstatic --noinput

echo "Static files collected - Статические файлы собраны"

echo "Starting Django application - Запускаем Django приложение"
