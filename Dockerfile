# CloudMercury website
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect CSS, JS and images into staticfiles/ so WhiteNoise can serve them.
RUN python manage.py collectstatic --noinput

EXPOSE 8001

# Migrations run when the container starts (the Postgres database isn't reachable at build time).
# Settings such as DATABASE_URL come from the environment, e.g. `docker run --env-file .env ...`
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:8001 --workers 3 --timeout 60"]

# Build and push:
#   docker build -t cloudmercury:v3 .
#   docker run --env-file .env -p 8001:8001 -v cloudmercury-media:/app/backend/media cloudmercury:v3
#   docker tag cloudmercury:v3 gcr.io/cloudinovater/cloudmercury:v3
#   docker push gcr.io/cloudinovater/cloudmercury:v3
