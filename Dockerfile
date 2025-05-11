# Dockerfile
FROM python:3.11-slim

# Install psycopg2 deps + netcat-openbsd so "nc" is available
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential libpq-dev netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install your Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your source
COPY . .

# Ensure we use the right settings and no buffering
ENV DJANGO_SETTINGS_MODULE=djangoProject3.settings
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# On container start, wait for Postgres, migrate, collectstatic, then launch Gunicorn
CMD ["sh", "-c", "\
    until nc -z $DATABASE_HOST $DATABASE_PORT; do echo 'Waiting for Postgres…'; sleep 1; done && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn djangoProject3.wsgi:application --bind 0.0.0.0:8000 --workers 2 \
"]
