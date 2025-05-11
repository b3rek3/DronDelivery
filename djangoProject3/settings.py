import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env в корне проекта
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ------------------------------------------------------------------------------
# Общие настройки
# ------------------------------------------------------------------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

# DEBUG включаем/выключаем через env: DEBUG=True/False
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')

# ALLOWED_HOSTS из env, через запятую
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]

# Приложения
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Ваши
    'core',
    'api',
    # Сторонние
    'rest_framework',
    'drf_spectacular',
    # Профилирование
    'silk',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise сразу после Security
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Silk profiling (в проде можно отключить через DEBUG)
    'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'djangoProject3.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoProject3.wsgi.application'
# (если используете ASGI)
# ASGI_APPLICATION = 'djangoProject3.asgi.application'

# ------------------------------------------------------------------------------
# База данных
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.getenv('DATABASE_NAME', 'Dron'),
        'USER':     os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST':     os.getenv('DATABASE_HOST', 'localhost'),
        'PORT':     os.getenv('DATABASE_PORT', '5432'),
    }
}

# ------------------------------------------------------------------------------
# Кэш (Redis, если задан REDIS_URL)
# ------------------------------------------------------------------------------

if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND':  'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
        }
    }

# ------------------------------------------------------------------------------
# Авторизация REST Framework
# ------------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'core.throttles.BurstRateThrottle',
        'core.throttles.SustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':     '2/minute',
        'burst':    '2/minute',
        'sustained':'15/hour',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE':               'Fast Delivery API',
    'DESCRIPTION':         'Get your food delivered in minutes with our efficient drone service.',
    'VERSION':             '1.0.0',
    'SERVE_INCLUDE_SCHEMA': not DEBUG,
}

# ------------------------------------------------------------------------------
# Статика и медиа
# ------------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# для разработки
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Если настроен MinIO/S3
if os.getenv('MINIO_BUCKET'):
    INSTALLED_APPS += ['storages']
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_ENDPOINT_URL = os.getenv('MINIO_ENDPOINT')
    AWS_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('MINIO_BUCKET')
    AWS_S3_REGION_NAME = os.getenv('MINIO_REGION') or None
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'path'

# ------------------------------------------------------------------------------
# Локализация и время
# ------------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE =     os.getenv('TIME_ZONE', 'UTC')
USE_I18N =      True
USE_L10N =      True
USE_TZ =        True

# ------------------------------------------------------------------------------
# Пользовательская модель и авто-поля
# ------------------------------------------------------------------------------

AUTH_USER_MODEL = 'core.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------------------
# Пароли
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ------------------------------------------------------------------------------
# Логирование
# ------------------------------------------------------------------------------

LOGGING = {
    'version':                 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO')},
}

# ------------------------------------------------------------------------------
# Silk profiling — отключаем в проде
# ------------------------------------------------------------------------------

if not DEBUG:
    try:
        MIDDLEWARE.remove('silk.middleware.SilkyMiddleware')
        INSTALLED_APPS.remove('silk')
    except ValueError:
        pass
