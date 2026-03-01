#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install dependencies from the fixed requirements file
pip install -r requirements.txt

# 2. Download spaCy model (This avoids the 404 URL issue)
python -m spacy download en_core_web_sm

# 3. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# 4. Standard Django build commands
python manage.py collectstatic --no-input
python manage.py migrate