#!/bin/sh

echo "Running database migrations..."
flask db upgrade

if [ $? -ne 0 ]; then
    echo "Database migrations failed. Aborting startup."
    exit 1
fi

echo "Starting Flask app..."
exec python app.py
