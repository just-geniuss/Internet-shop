# Инструкция по установке и запуску проекта

## Системные требования

### Linux (Debian/Ubuntu)
```bash
# Установка Python и необходимых системных пакетов
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git libmagic1 postgresql postgresql-contrib python3-dev libpq-dev

# Если вы используете SQLite вместо PostgreSQL, можно не устанавливать postgresql и libpq-dev
```

### macOS
```bash
# Установка с помощью Homebrew
brew update
brew install python libmagic postgresql

# Если вы используете SQLite вместо PostgreSQL, можно не устанавливать postgresql
```

## Клонирование репозитория

```bash
git clone https://github.com/your-username/DjangoProject.git
cd DjangoProject
```

## Настройка окружения

### Создание и активация виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # На Linux/macOS
venv\Scripts\activate     # На Windows
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте файл .env, установив необходимые значения
```

## Настройка базы данных

### Создание и применение миграций
```bash
python manage.py migrate
```

### Создание суперпользователя (администратора)
```bash
python manage.py createsuperuser
```

### Загрузка демонстрационных данных (опционально)
```bash
python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json
```

## Запуск сервера для разработки

```bash
python manage.py runserver
```

Теперь вы можете открыть сайт по адресу: http://127.0.0.1:8000/

## Настройка для продакшена (на VPS/хостинге)

### Сбор статических файлов
```bash
python manage.py collectstatic
```

### Настройка Gunicorn и Nginx
Создайте конфигурационный файл для Gunicorn и Nginx согласно документации:
- [Настройка Gunicorn](https://docs.gunicorn.org/en/stable/deploy.html)
- [Настройка Nginx](https://nginx.org/en/docs/http/configuring_https_servers.html)

### Установка SSL-сертификата (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

## Проблемы и решения

### Ошибка с python-magic
Если вы получаете ошибку при импорте `magic`, попробуйте установить пакет libmagic:

**На Linux:**
```bash
sudo apt-get install libmagic1
```

**На macOS:**
```bash
brew install libmagic
```

**На Windows:**
Загрузите и установите DLL-файлы для libmagic, как описано в документации к python-magic: https://github.com/ahupp/python-magic#windows

### Ошибки при миграции
Если вы получаете ошибки во время миграции, попробуйте удалить файл базы данных (если используете SQLite) и создать его заново:
```bash
rm db.sqlite3  # Удаление базы данных SQLite (внимание: это удалит все данные!)
python manage.py migrate  # Создание новой базы данных и применение миграций
```

### Проблемы с медиа-файлами
Убедитесь, что директории `media` и `static` существуют и имеют правильные права доступа:
```bash
mkdir -p media static
chmod 755 media static
``` 