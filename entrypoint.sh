#!/bin/bash

# Wait for database
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@revline.com', 'admin123')
    print('Superuser created successfully!')
else:
    print('Superuser already exists')
EOF

# Collect static files
python manage.py collectstatic --noinput

# Start server
exec "$@"