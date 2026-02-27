#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Download the correct spaCy model (Reliable method)
python -m spacy download en_core_web_sm

# Download NLTK data (required for your utils.py)
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Convert static files for Whitenoise
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate