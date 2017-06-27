#!/bin/ash

if [ -z "$DJANGO_PORT" ]; then
  export DJANGO_PORT=8000
fi

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:${DJANGO_PORT}