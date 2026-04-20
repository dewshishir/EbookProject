#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Preparing database..."
mkdir -p staticfiles/database
cp db.sqlite3 staticfiles/database/
