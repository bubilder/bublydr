import os
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо змінні оточення
load_dotenv()

# Базова директорія проєкту
BASE_DIR = Path(__file__).resolve().parent.parent

# Налаштування безпеки
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонні бібліотеки
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Наші додатки
    'accounts',      
    'menu',  
    'tables',  
    'orders',  
    'payments',
    'inventory',  
    'dashboard',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bublydr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bublydr.wsgi.application'

# Налаштування бази даних
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'bublydr'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Валідація паролів
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Налаштування локалізації
LANGUAGE_CODE = 'uk-ua'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

# Статичні файли (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Медіа файли
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип первинного ключа за замовчуванням
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
# Користувацька модель для автентифікації
AUTH_USER_MODEL = 'accounts.User'

# Налаштування для входу
LOGIN_REDIRECT_URL = 'home'  # Куди перенаправляти після успішного входу
LOGIN_URL = 'accounts:login'  # Сторінка для входу
LOGOUT_REDIRECT_URL = 'accounts:login'  # Куди перенаправляти після виходу