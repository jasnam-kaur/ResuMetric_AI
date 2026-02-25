import fitz  # Standard for PyMuPDF 1.23.22
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy for Lemmatization
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Keep this function so views.py can find it!"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def clean_resume_text(text):
    """Advanced cleaning using NLP Lemmatization"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    
    # Process text through spaCy
    doc = nlp(text)
    # Reduces words to root (e.g., 'programming' -> 'program')
    lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    return lemmatized.strip()

def calculate_match_score(resume_text, jd_text):
    """Advanced similarity scoring"""
    if not resume_text or not jd_text:
        return 0.0
    
    # Clean both using new logic
    clean_resume = clean_resume_text(resume_text)
    clean_jd = clean_resume_text(jd_text)
    
    content = [clean_resume, clean_jd]
    # Recognizes multi-word skills like 'Machine Learning'
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    
    try:
        tfidf_matrix = vectorizer.fit_transform(content)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    except:
        return 0.0