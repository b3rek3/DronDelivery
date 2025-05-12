# djangoProject3/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# BASE & ENV
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ──────────────────────────────────────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]

# ──────────────────────────────────────────────────────────────────────────────
# APPS
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # your apps
    'core',
    'api',

    # 3rd-party
    'rest_framework',
    'drf_spectacular',
    'silk',
    'storages',
]

# ──────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE, URLS, WSGI
# ──────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'djangoProject3.urls'
WSGI_APPLICATION = 'djangoProject3.wsgi.application'

# ──────────────────────────────────────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.getenv('DATABASE_NAME'),
        'USER':     os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST':     os.getenv('DATABASE_HOST'),
        'PORT':     os.getenv('DATABASE_PORT'),
    }
}

# ──────────────────────────────────────────────────────────────────────────────
# TEMPLATES
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':    [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS':  {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# STATIC FILES
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL           = '/static/'
STATIC_ROOT          = BASE_DIR / 'staticfiles'
STATICFILES_DIRS     = [BASE_DIR / 'static']
STATICFILES_STORAGE  = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ──────────────────────────────────────────────────────────────────────────────
# MEDIA (local fallback)
# ──────────────────────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ──────────────────────────────────────────────────────────────────────────────
# MINIO / S3 STORAGE
# ──────────────────────────────────────────────────────────────────────────────
if os.getenv('MINIO_BUCKET'):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # inside Docker → MinIO
    AWS_S3_ENDPOINT_URL      = os.getenv('MINIO_INTERNAL_ENDPOINT')
    # how the browser fetches them
    AWS_S3_CUSTOM_DOMAIN     = os.getenv('MINIO_EXTERNAL_ENDPOINT')

    AWS_ACCESS_KEY_ID        = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY    = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME  = os.getenv('MINIO_BUCKET')
    AWS_S3_REGION_NAME       = os.getenv('MINIO_REGION')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE  = 'path'
    AWS_S3_FILE_OVERWRITE    = False
    AWS_DEFAULT_ACL          = None

    # point MEDIA_URL at your bucket
    MEDIA_URL = f"{AWS_S3_CUSTOM_DOMAIN}/media/"

# ──────────────────────────────────────────────────────────────────────────────
# REST FRAMEWORK & SPECTACULAR
# ──────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS':     'drf_spectacular.openapi.AutoSchema',
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

# ──────────────────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = os.getenv('TIME_ZONE', 'UTC')
USE_I18N      = True
USE_TZ        = True

# ──────────────────────────────────────────────────────────────────────────────
# AUTH & DEFAULT PK
# ──────────────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL    = 'core.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
