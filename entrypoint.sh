#!/bin/bash

# Wait for db to be ready
export PGPASSWORD=revline_pass
until pg_isready -h db -p 5432 -U revline_user -d revline_db; do
  echo "Waiting for database..."
  sleep 2
done

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start server
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000