#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

pip install spacy==3.7.2

pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

python manage.py collectstatic --no-input
python manage.py migrate