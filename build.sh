#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (this won't fail if the user already exists because we use --no-input)
# Note: Django 3.0+ handles the password from the env variable automatically
python manage.py createsuperuser --no-input || true
