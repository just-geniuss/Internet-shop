#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для генерации Django SECRET_KEY
generate_secret_key() {
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
print(secret_key)
"
}

# Функция для запроса ввода с возможностью значения по умолчанию
prompt_with_default() {
    local prompt_text="$1"
    local default_value="$2"
    local result
    
    if [ -n "$default_value" ]; then
        read -p "$prompt_text [$default_value]: " result
        echo "${result:-$default_value}"
    else
        read -p "$prompt_text: " result
        echo "$result"
    fi
}

# Функция для запроса пароля
prompt_password() {
    local prompt_text="$1"
    local result
    
    while true; do
        read -s -p "$prompt_text: " result
        echo ""
        
        if [ -z "$result" ]; then
            echo "Пароль не может быть пустым / Password cannot be empty"
            continue
        fi
        
        # Простая валидация - только основные символы, избегаем проблемных
        if [[ "$result" =~ [\'\"\\] ]]; then
            echo "Пароль не должен содержать кавычки или обратные слеши / Password should not contain quotes or backslashes"
            continue
        fi
        
        echo "$result"
        break
    done
}

# Функция для выбора языка
choose_language() {
    echo -e "${BLUE}Choose language / Выберите язык:${NC}"
    echo "1) English"
    echo "2) Русский"
    
    while true; do
        read -p "Enter choice (1-2): " lang_choice
        case $lang_choice in
            1) LANG="en"; break;;
            2) LANG="ru"; break;;
            *) echo "Please select 1 or 2 / Пожалуйста, выберите 1 или 2";;
        esac
    done
}

# Функция для локализованного вывода
localized_echo() {
    local en_text="$1"
    local ru_text="$2"
    
    if [ "$LANG" = "ru" ]; then
        echo -e "$ru_text"
    else
        echo -e "$en_text"
    fi
}

# Функция для локализованного запроса
localized_prompt() {
    local en_prompt="$1"
    local ru_prompt="$2"
    local default_value="$3"
    
    if [ "$LANG" = "ru" ]; then
        prompt_with_default "$ru_prompt" "$default_value"
    else
        prompt_with_default "$en_prompt" "$default_value"
    fi
}

# Функция для создания nginx конфигурации
create_nginx_config() {
    local domain="$1"
    
    cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    upstream web {
        server web:8899;
    }
    
    server {
        listen 80;
        server_name ${domain};
        
        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
        
        # Media files
        location /media/ {
            alias /var/www/media/;
            expires 7d;
            add_header Cache-Control "public";
        }
        
        # Django application
        location / {
            proxy_pass http://web;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Timeout settings
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF
}

# Основная функция
main() {
    clear
    
    # Выбор языка
    choose_language
    
    localized_echo "${GREEN}🚀 Internet Shop Setup Script${NC}" "${GREEN}🚀 Скрипт настройки интернет-магазина${NC}"
    localized_echo "${YELLOW}This script will help you configure your Django project${NC}" "${YELLOW}Этот скрипт поможет настроить ваш Django проект${NC}"
    echo ""
    
    # Проверка наличия .env файла
    if [ -f ".env" ]; then
        localized_echo "${YELLOW}Warning: .env file already exists!${NC}" "${YELLOW}Внимание: файл .env уже существует!${NC}"
        if [ "$LANG" = "ru" ]; then
            read -p "Перезаписать? (y/N): " overwrite
        else
            read -p "Overwrite? (y/N): " overwrite
        fi
        
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            localized_echo "Setup cancelled." "Настройка отменена."
            exit 0
        fi
    fi
    
    # Генерация SECRET_KEY
    localized_echo "${BLUE}Generating Django SECRET_KEY...${NC}" "${BLUE}Генерация Django SECRET_KEY...${NC}"
    SECRET_KEY=$(generate_secret_key)
    
    # Основные настройки
    localized_echo "\n${BLUE}Basic Settings / Основные настройки:${NC}" "\n${BLUE}Основные настройки:${NC}"
    
    DOMAIN=$(localized_prompt "Enter domain name" "Введите доменное имя" "localhost")
    
    if [ "$LANG" = "ru" ]; then
        echo "Выберите режим работы:"
        echo "1) Разработка (DEBUG=True)"
        echo "2) Продакшн (DEBUG=False)"
        read -p "Выберите режим (1-2): " mode_choice
    else
        echo "Choose mode:"
        echo "1) Development (DEBUG=True)"
        echo "2) Production (DEBUG=False)"
        read -p "Select mode (1-2): " mode_choice
    fi
    
    case $mode_choice in
        1) DEBUG="True"; MODE="dev";;
        2) DEBUG="False"; MODE="prod";;
        *) DEBUG="True"; MODE="dev";;
    esac
    
    # Настройки базы данных
    localized_echo "\n${BLUE}Database Settings / Настройки базы данных:${NC}" "\n${BLUE}Настройки базы данных:${NC}"
    
    DB_NAME=$(localized_prompt "Database name" "Имя базы данных" "autoparts_shop")
    DB_USER=$(localized_prompt "Database user" "Пользователь базы данных" "postgres")
    
    # Валидация имени базы данных и пользователя
    if [[ ! "$DB_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        localized_echo "${YELLOW}Warning: Database name should start with a letter and contain only letters, numbers, and underscores${NC}" "${YELLOW}Внимание: Имя базы данных должно начинаться с буквы и содержать только буквы, цифры и подчеркивания${NC}"
        DB_NAME="autoparts_shop"
    fi
    
    if [[ ! "$DB_USER" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        localized_echo "${YELLOW}Warning: Database user should start with a letter and contain only letters, numbers, and underscores${NC}" "${YELLOW}Внимание: Пользователь БД должен начинаться с буквы и содержать только буквы, цифры и подчеркивания${NC}"
        DB_USER="postgres"
    fi
    
    DB_PASSWORD=$(prompt_password "$(if [ "$LANG" = "ru" ]; then echo "Пароль базы данных"; else echo "Database password"; fi)")
    
    # Настройка nginx
    if [ "$MODE" = "prod" ]; then
        localized_echo "\n${BLUE}Nginx Configuration / Настройка Nginx:${NC}" "\n${BLUE}Настройка Nginx:${NC}"
        if [ "$LANG" = "ru" ]; then
            read -p "Создать конфигурацию Nginx? (Y/n): " create_nginx
        else
            read -p "Create Nginx configuration? (Y/n): " create_nginx
        fi
        
        if [[ ! "$create_nginx" =~ ^[Nn]$ ]]; then
            CREATE_NGINX="true"
        else
            CREATE_NGINX="false"
        fi
    else
        CREATE_NGINX="false"
    fi
    
    # Настройка интеграции с 1С
    localized_echo "\n${BLUE}1C Integration Settings (Optional) / Настройки интеграции с 1С (опционально):${NC}" "\n${BLUE}Настройки интеграции с 1С (опционально):${NC}"
    if [ "$LANG" = "ru" ]; then
        read -p "Настроить интеграцию с 1С? (y/N): " setup_1c
    else
        read -p "Setup 1C integration? (y/N): " setup_1c
    fi
    
    if [[ "$setup_1c" =~ ^[Yy]$ ]]; then
        INTEGRATION_1C_TOKEN=$(localized_prompt "1C integration token" "Токен интеграции с 1С" "your-secure-token-for-1c-integration")
    else
        INTEGRATION_1C_TOKEN="your-secure-token-for-1c-integration"
    fi
    
    # Настройка email
    localized_echo "\n${BLUE}Email Settings (Optional) / Настройки почты (опционально):${NC}" "\n${BLUE}Настройки почты (опционально):${NC}"
    if [ "$LANG" = "ru" ]; then
        read -p "Настроить отправку email? (y/N): " setup_email
    else
        read -p "Setup email sending? (y/N): " setup_email
    fi
    
    if [[ "$setup_email" =~ ^[Yy]$ ]]; then
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
        EMAIL_HOST=$(localized_prompt "SMTP host" "SMTP хост" "smtp.gmail.com")
        EMAIL_PORT=$(localized_prompt "SMTP port" "SMTP порт" "587")
        EMAIL_USE_TLS=$(localized_prompt "Use TLS (True/False)" "Использовать TLS (True/False)" "True")
        EMAIL_HOST_USER=$(localized_prompt "Email address" "Email адрес" "")
        EMAIL_HOST_PASSWORD=$(prompt_password "$(if [ "$LANG" = "ru" ]; then echo "Email пароль"; else echo "Email password"; fi)")
        DEFAULT_FROM_EMAIL=$(localized_prompt "Default from email" "Email отправителя по умолчанию" "$EMAIL_HOST_USER")
    else
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
        EMAIL_HOST="smtp.example.com"
        EMAIL_PORT="587"
        EMAIL_USE_TLS="True"
        EMAIL_HOST_USER="your-email@example.com"
        EMAIL_HOST_PASSWORD="your-email-password"
        DEFAULT_FROM_EMAIL="noreply@example.com"
    fi
    
    # Создание .env файла
    localized_echo "\n${GREEN}Creating .env file...${NC}" "\n${GREEN}Создание .env файла...${NC}"
    
    # Безопасное создание .env файла с экранированием специальных символов
    {
        echo "# Общие настройки Django"
        echo "DEBUG=$DEBUG"
        echo "SECRET_KEY='$SECRET_KEY'"
        echo "ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,$DOMAIN"
        echo "DOMAIN=$DOMAIN"
        echo ""
        echo "# Настройки базы данных"
        echo "DB_ENGINE=django.db.backends.postgresql"
        echo "DB_NAME=$DB_NAME"
        echo "DB_USER=$DB_USER"
        echo "DB_PASSWORD='$DB_PASSWORD'"
        echo "DB_HOST=db"
        echo "DB_PORT=5432"
        echo ""
        echo "# Настройки для интеграции с 1С"
        echo "INTEGRATION_1C_TOKEN='$INTEGRATION_1C_TOKEN'"
        echo ""
        echo "# Настройки безопасности"
        if [ "$DEBUG" = "False" ]; then
            echo "SECURE_SSL_REDIRECT=True"
            echo "SESSION_COOKIE_SECURE=True"
            echo "CSRF_COOKIE_SECURE=True"
        else
            echo "SECURE_SSL_REDIRECT=False"
            echo "SESSION_COOKIE_SECURE=False"
            echo "CSRF_COOKIE_SECURE=False"
        fi
        echo ""
        echo "# Настройки для электронной почты"
        echo "EMAIL_BACKEND=$EMAIL_BACKEND"
        echo "EMAIL_HOST=$EMAIL_HOST"
        echo "EMAIL_PORT=$EMAIL_PORT"
        echo "EMAIL_USE_TLS=$EMAIL_USE_TLS"
        echo "EMAIL_HOST_USER=$EMAIL_HOST_USER"
        echo "EMAIL_HOST_PASSWORD='$EMAIL_HOST_PASSWORD'"
        echo "DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL"
        echo ""
        echo "# Максимальный размер загружаемых файлов (в байтах)"
        echo "MAX_UPLOAD_SIZE=5242880"
    } > .env
    
    # Создание nginx конфигурации если нужно
    if [ "$CREATE_NGINX" = "true" ]; then
        localized_echo "${GREEN}Creating Nginx configuration...${NC}" "${GREEN}Создание конфигурации Nginx...${NC}"
        create_nginx_config "$DOMAIN"
    fi
    
    # Запуск контейнеров
    localized_echo "\n${GREEN}Starting containers...${NC}" "\n${GREEN}Запуск контейнеров...${NC}"
    
    if [ "$MODE" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        if ! docker-compose -f docker-compose.prod.yml up --build -d; then
            localized_echo "${RED}Error: Failed to start containers${NC}" "${RED}Ошибка: Не удалось запустить контейнеры${NC}"
            exit 1
        fi
        COMPOSE_FILE="docker-compose.prod.yml"
    else
        docker-compose down 2>/dev/null || true
        if ! docker-compose up --build -d; then
            localized_echo "${RED}Error: Failed to start containers${NC}" "${RED}Ошибка: Не удалось запустить контейнеры${NC}"
            exit 1
        fi
        COMPOSE_FILE="docker-compose.yml"
    fi
    
    # Ожидание запуска контейнеров
    localized_echo "${YELLOW}Waiting for containers to start...${NC}" "${YELLOW}Ожидание запуска контейнеров...${NC}"
    
    # Проверка состояния контейнеров
    for i in {1..30}; do
        if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
            localized_echo "${GREEN}Containers are running${NC}" "${GREEN}Контейнеры запущены${NC}"
            break
        fi
        
        if [ $i -eq 30 ]; then
            localized_echo "${RED}Error: Containers failed to start properly${NC}" "${RED}Ошибка: Контейнеры не запустились правильно${NC}"
            localized_echo "${YELLOW}Checking logs...${NC}" "${YELLOW}Проверка логов...${NC}"
            docker-compose -f $COMPOSE_FILE logs web
            exit 1
        fi
        
        sleep 2
    done
    
    # Проверка готовности Django
    localized_echo "\n${BLUE}Checking Django readiness / Проверка готовности Django:${NC}" "\n${BLUE}Проверка готовности Django:${NC}"
    
    for i in {1..10}; do
        if [ "$MODE" = "prod" ]; then
            if docker-compose -f docker-compose.prod.yml exec -T web python manage.py check 2>/dev/null; then
                localized_echo "${GREEN}Django is ready${NC}" "${GREEN}Django готов${NC}"
                break
            fi
        else
            if docker-compose exec -T web python manage.py check 2>/dev/null; then
                localized_echo "${GREEN}Django is ready${NC}" "${GREEN}Django готов${NC}"
                break
            fi
        fi
        
        if [ $i -eq 10 ]; then
            localized_echo "${YELLOW}Django may not be fully ready, but continuing...${NC}" "${YELLOW}Django может быть не полностью готов, но продолжаем...${NC}"
            break
        fi
        
        localized_echo "${YELLOW}Waiting for Django to be ready...${NC}" "${YELLOW}Ожидание готовности Django...${NC}"
        sleep 3
    done
    
    
    # Финальные инструкции
    echo ""
    localized_echo "${GREEN}🎉 Setup completed successfully!${NC}" "${GREEN}🎉 Настройка завершена успешно!${NC}"
    echo ""
    
    if [ "$MODE" = "prod" ] && [ "$CREATE_NGINX" = "true" ]; then
        localized_echo "${BLUE}Your application is available at:${NC}" "${BLUE}Ваше приложение доступно по адресу:${NC}"
        echo "   http://127.0.0.1:8443"
        echo "   http://$DOMAIN:8443 (if configured in /etc/hosts)"
        echo ""
        SUPERUSER_CMD="docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
        DEMO_DATA_CMD="docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json fixtures/products.json fixtures/product_attributes.json fixtures/integration_settings.json"
    else
        localized_echo "${BLUE}Your application is available at:${NC}" "${BLUE}Ваше приложение доступно по адресу:${NC}"
        echo "   http://127.0.0.1:8899"
        echo ""
        SUPERUSER_CMD="docker-compose exec web python manage.py createsuperuser"
        DEMO_DATA_CMD="docker-compose exec web python manage.py loaddata fixtures/categories.json fixtures/manufacturers.json fixtures/cars.json fixtures/products.json fixtures/product_attributes.json fixtures/integration_settings.json"
    fi
    
    echo ""
    localized_echo "${YELLOW}Next steps / Следующие шаги:${NC}" "${YELLOW}Следующие шаги:${NC}"
    echo ""
    localized_echo "${BLUE}1. Create admin user / Создать администратора:${NC}" "${BLUE}1. Создать администратора:${NC}"
    echo "   $SUPERUSER_CMD"
    echo ""
    localized_echo "${BLUE}2. Load demo data (optional) / Загрузить демо данные (опционально):${NC}" "${BLUE}2. Загрузить демо данные (опционально):${NC}"
    echo "   $DEMO_DATA_CMD"
    echo ""
    localized_echo "${BLUE}3. Admin panel / Панель администратора:${NC}" "${BLUE}3. Панель администратора:${NC}"
    if [ "$MODE" = "prod" ] && [ "$CREATE_NGINX" = "true" ]; then
        echo "   http://127.0.0.1:8443/admin/"
    else
        echo "   http://127.0.0.1:8899/admin/"
    fi
    
    echo ""
    localized_echo "${YELLOW}Useful commands:${NC}" "${YELLOW}Полезные команды:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE logs -f web"
    echo "   docker-compose -f $COMPOSE_FILE down"
    echo "   docker-compose -f $COMPOSE_FILE restart web"
}

# Запуск основной функции
main "$@"
