# Dockerfile
FROM python:3.11-slim

# Системные зависимости для psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Django сам подхватит DJANGO_SETTINGS_MODULE из manage.py (по-умолчанию djangoProject3.settings)
ENV PYTHONUNBUFFERED=1

# Собираем статику (возьмёт STATIC_ROOT из settings.py)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запуск через gunicorn
CMD ["gunicorn", "djangoProject3.wsgi:application", "--bind", "0.0.0.0:8000"]
