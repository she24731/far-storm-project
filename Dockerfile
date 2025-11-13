# Dockerfile for Yale Newcomer Survival Guide
# Uses Python 3.11 for Django 5 compatibility

FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles /var/data /app/app_data

# Collect static files (WhiteNoise)
RUN python manage.py collectstatic --noinput || true

# Expose port 8000
EXPOSE 8000

# Run migrations, setup groups, seed data, and start gunicorn
# Using 1 worker to serialize writes for DuckDB
CMD python manage.py migrate && \
    python manage.py setup_groups && \
    (python manage.py seed_data || true) && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1
