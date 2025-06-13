#!/bin/bash

# Функция для генерации SECRET_KEY
generate_secret_key() {
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
print(secret_key)
"
}

# Функция для выбора языка
choose_language() {
    echo "Choose language / Выберите язык:"
    echo "1) English"
    echo "2) Русский"
    read -p "Enter choice (1-2): " lang_choice
    
    case $lang_choice in
        1) LANGUAGE="en" ;;
        2) LANGUAGE="ru" ;;
        *) 
            echo "Invalid choice. Using English by default."
            LANGUAGE="en" 
            ;;
    esac
}

# Функции для текста на разных языках
get_text() {
    case $1 in
        "welcome")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "🛠️  Добро пожаловать в мастер настройки интернет-магазина автозапчастей!"
            else
                echo "🛠️  Welcome to the Auto Parts Shop setup wizard!"
            fi
            ;;
        "choose_mode")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Выберите режим развертывания:"
                echo "1) Разработка (DEBUG=True)"
                echo "2) Продакшн (DEBUG=False)"
            else
                echo "Choose deployment mode:"
                echo "1) Development (DEBUG=True)"
                echo "2) Production (DEBUG=False)"
            fi
            ;;
        "enter_choice")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите выбор (1-2): "
            else
                echo "Enter choice (1-2): "
            fi
            ;;
        "db_config")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "📊 Настройка базы данных"
            else
                echo "📊 Database configuration"
            fi
            ;;
        "db_name")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите название базы данных [autoparts_shop]: "
            else
                echo "Enter database name [autoparts_shop]: "
            fi
            ;;
        "db_user")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите имя пользователя БД [postgres]: "
            else
                echo "Enter database user [postgres]: "
            fi
            ;;
        "db_password")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите пароль БД [postgres]: "
            else
                echo "Enter database password [postgres]: "
            fi
            ;;
        "email_setup")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "📧 Настройка электронной почты"
                echo "Хотите настроить отправку email? (y/n) [n]: "
            else
                echo "📧 Email configuration"
                echo "Do you want to configure email sending? (y/n) [n]: "
            fi
            ;;
        "email_host")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите SMTP сервер: "
            else
                echo "Enter SMTP server: "
            fi
            ;;
        "email_port")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите SMTP порт [587]: "
            else
                echo "Enter SMTP port [587]: "
            fi
            ;;
        "email_user")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите email пользователя: "
            else
                echo "Enter email user: "
            fi
            ;;
        "email_password")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите email пароль: "
            else
                echo "Enter email password: "
            fi
            ;;
        "integration_1c")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "🔗 Интеграция с 1С"
                echo "Хотите настроить интеграцию с 1С? (y/n) [n]: "
            else
                echo "🔗 1C Integration"
                echo "Do you want to configure 1C integration? (y/n) [n]: "
            fi
            ;;
        "integration_token")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "Введите токен для интеграции с 1С: "
            else
                echo "Enter 1C integration token: "
            fi
            ;;
        "creating_env")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "📄 Создание .env файла..."
            else
                echo "📄 Creating .env file..."
            fi
            ;;
        "starting_containers")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "🐳 Запуск Docker контейнеров..."
            else
                echo "🐳 Starting Docker containers..."
            fi
            ;;
        "applying_migrations")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "📦 Применение миграций базы данных..."
            else
                echo "📦 Applying database migrations..."
            fi
            ;;
        "loading_fixtures")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "📋 Загрузка демонстрационных данных..."
            else
                echo "📋 Loading demo data..."
            fi
            ;;
        "create_superuser")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "👤 Создание суперпользователя..."
                echo "Сейчас вам нужно будет создать администратора сайта."
            else
                echo "👤 Creating superuser..."
                echo "Now you need to create a site administrator."
            fi
            ;;
        "setup_complete")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "✅ Настройка завершена!"
                echo ""
                echo "🌐 Ваш интернет-магазин доступен по адресу: http://127.0.0.1:8443"
                echo "🔧 Административная панель: http://127.0.0.1:8443/admin/"
                echo ""
                echo "Полезные команды:"
                echo "  Остановить: docker-compose down"
                echo "  Логи: docker-compose logs -f web"
                echo "  Перезапустить: docker-compose restart"
            else
                echo "✅ Setup complete!"
                echo ""
                echo "🌐 Your shop is available at: http://127.0.0.1:8443"
                echo "🔧 Admin panel: http://127.0.0.1:8443/admin/"
                echo ""
                echo "Useful commands:"
                echo "  Stop: docker-compose down"
                echo "  Logs: docker-compose logs -f web"
                echo "  Restart: docker-compose restart"
            fi
            ;;
        "error")
            if [ "$LANGUAGE" = "ru" ]; then
                echo "❌ Ошибка: "
            else
                echo "❌ Error: "
            fi
            ;;
    esac
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "$(get_text "error")Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "$(get_text "error")Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
}

# Основная функция
main() {
    clear
    choose_language
    clear
    
    echo "$(get_text "welcome")"
    echo "=================================="
    echo ""
    
    # Проверка Docker
    check_docker
    
    # Выбор режима
    echo "$(get_text "choose_mode")"
    read -p "$(get_text "enter_choice")" mode_choice
    
    case $mode_choice in
        1) 
            DEBUG_MODE="True"
            COMPOSE_FILE="docker-compose.yml"
            SSL_REDIRECT="False"
            COOKIE_SECURE="False"
            ;;
        2) 
            DEBUG_MODE="False"
            COMPOSE_FILE="docker-compose.prod.yml"
            SSL_REDIRECT="True"
            COOKIE_SECURE="True"
            ;;
        *) 
            echo "Invalid choice. Using development mode."
            DEBUG_MODE="True"
            COMPOSE_FILE="docker-compose.yml"
            SSL_REDIRECT="False"
            COOKIE_SECURE="False"
            ;;
    esac
    
    echo ""
    echo "$(get_text "db_config")"
    echo "-------------------------"
    
    read -p "$(get_text "db_name")" DB_NAME
    DB_NAME=${DB_NAME:-autoparts_shop}
    
    read -p "$(get_text "db_user")" DB_USER
    DB_USER=${DB_USER:-postgres}
    
    read -s -p "$(get_text "db_password")" DB_PASSWORD
    DB_PASSWORD=${DB_PASSWORD:-postgres}
    echo ""
    
    # Настройка email
    echo ""
    read -p "$(get_text "email_setup")" setup_email
    if [[ $setup_email =~ ^[Yy]$ ]]; then
        read -p "$(get_text "email_host")" EMAIL_HOST
        read -p "$(get_text "email_port")" EMAIL_PORT
        EMAIL_PORT=${EMAIL_PORT:-587}
        read -p "$(get_text "email_user")" EMAIL_USER
        read -s -p "$(get_text "email_password")" EMAIL_PASSWORD
        echo ""
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
        EMAIL_USE_TLS="True"
        DEFAULT_FROM_EMAIL=${EMAIL_USER}
    else
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
        EMAIL_HOST=""
        EMAIL_PORT="587"
        EMAIL_USER=""
        EMAIL_PASSWORD=""
        EMAIL_USE_TLS="True"
        DEFAULT_FROM_EMAIL="noreply@example.com"
    fi
    
    # Настройка интеграции с 1С
    echo ""
    read -p "$(get_text "integration_1c")" setup_1c
    if [[ $setup_1c =~ ^[Yy]$ ]]; then
        read -p "$(get_text "integration_token")" INTEGRATION_TOKEN
    else
        INTEGRATION_TOKEN="your-secure-token-for-1c-integration"
    fi
    
    # Генерация SECRET_KEY
    SECRET_KEY=$(generate_secret_key)
    
    # Создание .env файла
    echo ""
    echo "$(get_text "creating_env")"
    
cat > .env << EOF
# Django настройки
DEBUG=${DEBUG_MODE}
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# База данных
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=db
DB_PORT=5432

# Настройки безопасности
SECURE_SSL_REDIRECT=${SSL_REDIRECT}
SESSION_COOKIE_SECURE=${COOKIE_SECURE}
CSRF_COOKIE_SECURE=${COOKIE_SECURE}

# Email настройки
EMAIL_BACKEND=${EMAIL_BACKEND}
EMAIL_HOST=${EMAIL_HOST}
EMAIL_PORT=${EMAIL_PORT}
EMAIL_USE_TLS=${EMAIL_USE_TLS}
EMAIL_HOST_USER=${EMAIL_USER}
EMAIL_HOST_PASSWORD=${EMAIL_PASSWORD}
DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL}

# Интеграция с 1С
INTEGRATION_1C_TOKEN=${INTEGRATION_TOKEN}

# Прочие настройки
MAX_UPLOAD_SIZE=5242880
EOF
    
    # Запуск контейнеров
    echo "$(get_text "starting_containers")"
    docker-compose -f $COMPOSE_FILE up --build -d
    
    # Ожидание запуска БД
    echo "$(get_text "applying_migrations")"
    sleep 10
    
    # Загрузка демонстрационных данных
    echo "$(get_text "loading_fixtures")"
    docker-compose -f $COMPOSE_FILE exec -T web python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json fixtures/products.json fixtures/product_attributes.json fixtures/integration_settings.json 2>/dev/null || true
    
    # Создание суперпользователя
    echo ""
    echo "$(get_text "create_superuser")"
    echo "=================================="
    docker-compose -f $COMPOSE_FILE exec web python manage.py createsuperuser
    
    # Завершение
    echo ""
    echo "$(get_text "setup_complete")"
}

# Запуск основной функции
main
