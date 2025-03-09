# Инструкции по развертыванию интернет-магазина автозапчастей

В этом документе описаны шаги по полному развертыванию интернет-магазина автозапчастей с нуля, включая настройку сервера, базы данных, веб-сервера и SSL-сертификатов.

## Содержание

1. [Подготовка сервера](#1-подготовка-сервера)
2. [Установка зависимостей](#2-установка-зависимостей)
3. [Клонирование репозитория](#3-клонирование-репозитория)
4. [Настройка окружения](#4-настройка-окружения)
5. [Настройка базы данных](#5-настройка-базы-данных)
6. [Настройка статических файлов](#6-настройка-статических-файлов)
7. [Настройка Gunicorn](#7-настройка-gunicorn)
8. [Настройка Nginx](#8-настройка-nginx)
9. [Настройка SSL с Certbot](#9-настройка-ssl-с-certbot)
10. [Запуск проекта](#10-запуск-проекта)
11. [Настройка автоматического обновления](#11-настройка-автоматического-обновления)
12. [Устранение неполадок](#12-устранение-неполадок)

## 1. Подготовка сервера

### Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### Установка необходимых пакетов

```bash
sudo apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib python3-dev libpq-dev certbot python3-certbot-nginx
```

### Создание пользователя (опционально)

```bash
sudo useradd -m -s /bin/bash shopuser
sudo passwd shopuser
sudo usermod -aG sudo shopuser
```

## 2. Установка зависимостей

### Настройка Python и виртуального окружения

```bash
cd /var/www
sudo mkdir shop
sudo chown -R $USER:$USER shop
cd shop
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

## 3. Клонирование репозитория

```bash
git clone https://github.com/just-geniuss/Internet-shop.git .
```

## 4. Настройка окружения

### Установка зависимостей проекта

```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Создание файла .env

```bash
nano .env
```

Добавьте следующее содержимое (замените значения на свои):

```
DEBUG=False
SECRET_KEY=вашсекретныйключ
ALLOWED_HOSTS=shop.justgeniuss.me,localhost,127.0.0.1
DATABASE_URL=postgres://username:password@localhost:5432/shop_db
1C_CONNECTION_STRING=http://example.com/1c/exchange
1C_USERNAME=admin_1c
1C_PASSWORD=secure_password
```

## 5. Настройка базы данных

### Создание PostgreSQL базы данных и пользователя

```bash
sudo -u postgres psql
```

В интерактивной оболочке PostgreSQL:

```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'надежныйпароль';
ALTER ROLE shop_user SET client_encoding TO 'utf8';
ALTER ROLE shop_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE shop_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
\q
```

### Миграция базы данных и создание суперпользователя

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Загрузка демонстрационных данных

```bash
python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json fixtures/products.json fixtures/product_attributes.json fixtures/integration_settings.json
```

## 6. Настройка статических файлов

### Сбор статических файлов

```bash
python manage.py collectstatic
```

## 7. Настройка Gunicorn

### Создание systemd конфигурации для Gunicorn

```bash
sudo nano /etc/systemd/system/gunicorn_shop.service
```

Добавьте следующее содержимое:

```ini
[Unit]
Description=gunicorn daemon for shop
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shop
ExecStart=/var/www/shop/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/shop/shop.sock DjangoProject.wsgi:application
Restart=on-failure
RestartSec=5s
Environment="PATH=/var/www/shop/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
```

### Запуск и активация Gunicorn

```bash
sudo systemctl start gunicorn_shop
sudo systemctl enable gunicorn_shop
sudo systemctl status gunicorn_shop
```

## 8. Настройка Nginx

### Создание конфигурации для сайта

```bash
sudo nano /etc/nginx/sites-available/shop
```

Добавьте следующее содержимое:

```nginx
server {
    listen 80;
    server_name shop.justgeniuss.me;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/shop;
    }
    
    location /media/ {
        root /var/www/shop;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/shop/shop.sock;
    }
}
```

### Активация конфигурации сайта

```bash
sudo ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 9. Настройка SSL с Certbot

### Получение и настройка SSL-сертификата

```bash
sudo certbot --nginx -d shop.justgeniuss.me
```

Следуйте инструкциям Certbot для завершения процесса.

Certbot автоматически изменит конфигурацию Nginx, добавив настройки SSL. Вот примерный вид обновленной конфигурации:

```nginx
server {
    listen 80;
    server_name shop.justgeniuss.me;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name shop.justgeniuss.me;

    ssl_certificate /etc/letsencrypt/live/shop.justgeniuss.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shop.justgeniuss.me/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/shop;
    }
    
    location /media/ {
        root /var/www/shop;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/shop/shop.sock;
    }
}
```

### Настройка автоматического обновления сертификата

Certbot автоматически добавляет задание cron для обновления сертификатов. Вы можете проверить это, запустив:

```bash
sudo systemctl status certbot.timer
```

## 10. Запуск проекта

### Перезапуск сервисов

```bash
sudo systemctl restart gunicorn_shop
sudo systemctl restart nginx
```

### Проверка работоспособности

Откройте в браузере https://shop.justgeniuss.me

## 11. Настройка автоматического обновления

### Создание скрипта для обновления приложения

```bash
nano /var/www/shop/update.sh
```

Добавьте следующее содержимое:

```bash
#!/bin/bash

cd /var/www/shop
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_shop
```

Разрешите выполнение скрипта:

```bash
chmod +x /var/www/shop/update.sh
```

### Настройка Cron для автоматического обновления (опционально)

```bash
sudo crontab -e
```

Добавьте следующую строку для обновления проекта каждый день в 3:00:

```
0 3 * * * /var/www/shop/update.sh >> /var/log/shop_update.log 2>&1
```

## 12. Устранение неполадок

### Проверка логов Gunicorn

```bash
sudo journalctl -u gunicorn_shop
```

### Проверка логов Nginx

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Проверка прав доступа

```bash
sudo chown -R www-data:www-data /var/www/shop
sudo chmod -R 755 /var/www/shop
```

### Проверка соединения с базой данных

```bash
source /var/www/shop/venv/bin/activate
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Connected!')"
```

### Перезапуск всех сервисов

```bash
sudo systemctl restart postgresql
sudo systemctl restart gunicorn_shop
sudo systemctl restart nginx
```

## Дополнительные настройки

### Настройка резервного копирования базы данных

Создание скрипта для резервного копирования:

```bash
nano /var/www/shop/backup.sh
```

Содержимое скрипта:

```bash
#!/bin/bash

DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/var/backups/shop"

mkdir -p $BACKUP_DIR

# Резервное копирование базы данных
pg_dump -U shop_user shop_db > $BACKUP_DIR/shop_db_$DATE.sql

# Сжатие резервной копии
gzip $BACKUP_DIR/shop_db_$DATE.sql

# Удаление копий старше 30 дней
find $BACKUP_DIR -name "shop_db_*.sql.gz" -mtime +30 -delete
```

Разрешите выполнение скрипта:

```bash
chmod +x /var/www/shop/backup.sh
```

Настройка Cron для автоматического резервного копирования:

```bash
sudo crontab -e
```

Добавьте следующую строку для создания резервной копии каждый день в 2:00:

```
0 2 * * * /var/www/shop/backup.sh >> /var/log/shop_backup.log 2>&1
```

### Настройка мониторинга (опционально)

```bash
sudo apt install -y prometheus-node-exporter
```

## Заключение

Следуя этим инструкциям, вы успешно развернули интернет-магазин автозапчастей на вашем сервере с доменом shop.justgeniuss.me. Сайт защищен SSL-сертификатом, обслуживается Nginx и Gunicorn, и использует базу данных PostgreSQL.

Рекомендуется регулярно проверять наличие обновлений для всех компонентов системы и применять их своевременно для обеспечения безопасности и стабильности работы магазина. 