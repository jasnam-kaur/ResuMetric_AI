#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# This command replaces the need for that broken URL
python -m spacy download en_core_web_sm

python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"
python manage.py collectstatic --no-input
python manage.py migrate