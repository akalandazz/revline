#!/bin/bash

# Wait for db to be ready
export PGPASSWORD=$DB_PASSWORD
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME; do
  echo "Waiting for database..."
  sleep 2
done

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Compile translation messages
echo "Compiling translation messages..."
python manage.py compilemessages

# Collect static files
python manage.py collectstatic --noinput

# Start server
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000