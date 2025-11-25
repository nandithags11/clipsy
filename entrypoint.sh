#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superusers if needed..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Create admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser admin already exists')

# Create testuser
if not User.objects.filter(username='testuser').exists():
    User.objects.create_superuser('testuser', 'testuser@example.com', 'testpass123')
    print('Superuser created: testuser/testpass123')
else:
    print('Superuser testuser already exists')
EOF

exec "$@"
