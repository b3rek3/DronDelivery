FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=dronproject.settings
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "dronproject.wsgi:application", "--bind", "0.0.0.0:8000"]
