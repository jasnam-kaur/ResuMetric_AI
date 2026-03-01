#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install base requirements
pip install -r requirements.txt

# 2. Install spaCy separately
pip install spacy==3.7.2

# 3. Direct install of the model wheel (This bypasses the 404 URL search)
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

# 4. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# 5. Django Production Setup
python manage.py collectstatic --no-input
python manage.py migrate