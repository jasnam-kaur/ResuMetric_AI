import pymupdf
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def clean_resume_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text) # Remove extra whitespace
    text = re.sub(r'[^a-z0-9\s]', '', text) # Remove special chars
    return text.strip()

def calculate_match_score(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0.0
    
    # We add a small 'buffer' of common words if strings are too short
    content = [resume_text, jd_text]
    
    vectorizer = TfidfVectorizer(stop_words='english') # Ignore words like 'the', 'is'
    try:
        tfidf_matrix = vectorizer.fit_transform(content)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]) * 100, 2)
    except:
        return 0.0