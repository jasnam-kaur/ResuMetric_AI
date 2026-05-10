import fitz  # PyMuPDF [cite: 85, 126]
import re
import spacy # [cite: 89, 125]
from sklearn.feature_extraction.text import TfidfVectorizer # [cite: 91, 125]
from sklearn.metrics.pairwise import cosine_similarity # [cite: 92, 125]

# Pre-load the model into memory to eliminate cold-start latency [cite: 106, 132]
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file using PyMuPDF[cite: 85]."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def clean_and_lemmatize(text):
    """
    Normalizes text for NLP processing[cite: 89, 90].
    Resolves the 'Parentheses Bug' via pre-tokenization regex[cite: 87, 88].
    """
    # 1. Standardize case and resolve parentheses bug [cite: 87, 170]
    text = text.lower().replace('(', ' ').replace(')', ' ') 
    
    # 2. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # 3. Lemmatization via spaCy [cite: 89, 90]
    doc = nlp(text)
    lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    
    return lemmatized.strip()

def calculate_cosine_sim(resume_text, jd_text):
    """Computes TF-IDF vectorization and Cosine Similarity[cite: 91, 92]."""
    # Use bigrams to capture phrases like "Machine Learning" [cite: 91]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def execute_industry_screening(resume_text, jd_text):
    """
    Core AI Matching Logic.
    Compares resume keywords against JD keywords.
    """
    # 1. Clean and tokenize text (Simple NLP approach)
    def get_keywords(text):
        # Removes special characters and converts to lowercase set
        return set(re.findall(r'\b\w{3,}\b', text.lower()))

    resume_words = get_keywords(resume_text)
    jd_words = get_keywords(jd_text)

    # 2. Identify Matches and Gaps
    matched_skills = list(resume_words.intersection(jd_words))
    missing_skills = list(jd_words - resume_words)

    # 3. Calculate Score
    if not jd_words:
        score = 0
    else:
        # Score = (Matches / Total JD Requirements) * 100
        score = round((len(matched_skills) / len(jd_words)) * 100, 1)

    return {
        'score': score,
        'matched': matched_skills,
        'missing': missing_skills,
        # We also include 'matched_skills' as an alias for the suggested_rooms view
        'matched_skills': matched_skills 
    }