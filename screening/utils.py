import fitz
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the spaCy model you installed on Render
nlp = spacy.load("en_core_web_sm")

def clean_resume_text(text):
    # 1. Basic Cleaning
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    
    # 2. NLP Lemmatization: Convert words to their base form
    doc = nlp(text)
    # This keeps only alphabetic words and removes "stop words" (is, the, etc.)
    lemmatized_text = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    
    return lemmatized_text.strip()

def calculate_match_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0.0
    
    # Clean both texts using the new Lemmatization logic
    clean_resume = clean_resume_text(resume_text)
    clean_jd = clean_resume_text(jd_text)
    
    content = [clean_resume, clean_jd]
    
    # We use ngram_range=(1,2) so it recognizes "Machine Learning" as one concept
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    
    try:
        tfidf_matrix = vectorizer.fit_transform(content)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    except Exception as e:
        print(f"ML Error: {e}")
        return 0.0