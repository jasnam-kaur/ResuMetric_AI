#!/usr/bin/env bash
set -o errexit

# 1. Install standard requirements
pip install -r requirements.txt

# 2. Force install the specific spaCy model directly
# This bypasses URL resolution issues in requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

# 3. Rest of your build commands
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"
python manage.py collectstatic --no-input
python manage.py migrate