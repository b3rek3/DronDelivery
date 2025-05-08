import os
from pathlib import Path

# ────────────────────────────────────────────────────────────
# BASE DIR
# ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ────────────────────────────────────────────────────────────
# SECURITY
# ────────────────────────────────────────────────────────────
SECRET_KEY = 'change-me-in-prod'
DEBUG      = True
ALLOWED_HOSTS = ['*']

# ────────────────────────────────────────────────────────────
# APPS
# ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'drf_yasg',
    'silk',
    'corsheaders',
    'django_celery_results',

    # Your app
    'app',
]

# ────────────────────────────────────────────────────────────
# MIDDLEWARE
# ────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'silk.middleware.SilkyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ────────────────────────────────────────────────────────────
# URLS & WSGI/ASGI
# ────────────────────────────────────────────────────────────
ROOT_URLCONF = 'dronproject.urls'
WSGI_APPLICATION = 'dronproject.wsgi.application'
ASGI_APPLICATION = 'dronproject.asgi.application'

# ────────────────────────────────────────────────────────────
# TEMPLATES
# ────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'app' / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ────────────────────────────────────────────────────────────
# DATABASE (SQLite для быстрой отладки)
# ────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   BASE_DIR / 'db.sqlite3',
    }
}

# ────────────────────────────────────────────────────────────
# AUTH
# ────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'app.User'

# ────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ────────────────────────────────────────────────────────────
# I18N & TIMEZONE
# ────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE     = 'Asia/Almaty'
USE_I18N      = True
USE_L10N      = True
USE_TZ        = True

# ────────────────────────────────────────────────────────────
# STATIC & MEDIA
# ────────────────────────────────────────────────────────────
STATIC_URL   = '/static/'
STATIC_ROOT  = BASE_DIR / 'static'
MEDIA_URL    = '/media/'
MEDIA_ROOT   = BASE_DIR / 'media'

# ────────────────────────────────────────────────────────────
# DRF + THROTTLING
# ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '1000/day',
    },
}

# ────────────────────────────────────────────────────────────
# SWAGGER / drf-yasg
# ────────────────────────────────────────────────────────────
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR':      True,
}

# ────────────────────────────────────────────────────────────
# CORS
# ────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ────────────────────────────────────────────────────────────
# SILK PROFILING
# ────────────────────────────────────────────────────────────
SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION  = True

# ────────────────────────────────────────────────────────────
# CELERY
# ────────────────────────────────────────────────────────────
CELERY_BROKER_URL     = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'

# ────────────────────────────────────────────────────────────
# DEFAULT PK FIELD
# ────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
