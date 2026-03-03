import fitz  # Standard for PyMuPDF
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy for Lemmatization [cite: 1]
nlp = spacy.load("en_core_web_sm")

# --- 1. Synonym Mapping ---
# Maps technical terms to broader categories to ensure high-accuracy matching.
SYNONYM_MAP = {
    'django': ['web framework', 'python backend', 'mvc'],
    'react': ['frontend', 'javascript library', 'spa', 'web development'],
    'docker': ['containerization', 'devops', 'kubernetes'],
    'aws': ['cloud computing', 'amazon web services', 'cloud infrastructure'],
    'postgresql': ['sql', 'relational database', 'postgres', 'dbms'],
    'scikit-learn': ['machine learning', 'data science', 'ai'],
    'tensorflow': ['deep learning', 'neural networks', 'ai'],
    'agile': ['scrum', 'kanban', 'project management'],
}

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def clean_resume_text(text):
    """
    Advanced cleaning using NLP Lemmatization.
    Fixes the 'Python(Basics)' issue by replacing parentheses with spaces.
    """
    text = text.lower()
    
    # CRITICAL FIX: Replace parentheses with spaces so 'Python(Basics)' becomes 'python basics' 
    text = text.replace('(', ' ').replace(')', ' ') 
    
    # Remove extra whitespace [cite: 1]
    text = re.sub(r'\s+', ' ', text)
    
    # Process text through spaCy [cite: 1]
    doc = nlp(text)
    
    # Lemmatize and remove stop words/punctuation [cite: 1]
    lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    return lemmatized.strip()

def calculate_match_score(resume_text, jd_text):
    """Calculates a weighted match score and identifies missing skills."""
    if not resume_text or not jd_text:
        return 0.0, []
    
    clean_resume = clean_resume_text(resume_text)
    clean_jd = clean_resume_text(jd_text)
    
    # Skill Extraction [cite: 1]
    resume_skills_str = extract_skills(resume_text)
    jd_skills_str = extract_skills(jd_text)
    
    resume_skills = set(resume_skills_str.split(", ")) if resume_skills_str != "No skills identified" else set()
    jd_skills = set(jd_skills_str.split(", ")) if jd_skills_str != "No skills identified" else set()
    
    # Identify Missing Skills (Set Difference) [cite: 1]
    missing_skills = list(jd_skills.difference(resume_skills))
    
    # 1. Base TF-IDF Similarity (60% weight) [cite: 1]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
    base_similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]) * 100
    
    # 2. Hard Skill Matcher (40% weight) [cite: 1]
    skill_match_ratio = len(resume_skills.intersection(jd_skills)) / len(jd_skills) if jd_skills else 0
    
    final_score = (base_similarity * 0.6) + (skill_match_ratio * 100 * 0.4)
    
    # Return both the score and the sorted list of missing items [cite: 1]
    return round(min(final_score, 100.0), 2), sorted(missing_skills)

def extract_skills(text):
    """Matches text against the Global Skill DB using lemmatization and synonyms."""
    text_lower = text.lower()
    
    # Pre-clean the text for matching 
    processed_text = text_lower.replace('(', ' ').replace(')', ' ')
    doc = nlp(processed_text)
    lemmatized_text = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    
    # The Global Skill DB [cite: 1]
    SKILL_DB = [
        # --- IT, CLOUD & DEVOPS ---
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible', 'Puppet', 
        'Chef', 'Cloud Computing', 'CI/CD', 'Linux', 'Unix', 'Bash', 'Shell Scripting', 'Virtualization', 
        'VMware', 'OpenStack', 'DevOps', 'SRE', 'JMeter', 'Nagios', 'Prometheus', 'Grafana', 
        'Microservices', 'Serverless', 'Lambda', 'EC2', 'S3', 'CloudFront', 'Route53',

        # --- SOFTWARE & WEB DEVELOPMENT ---
        'Python', 'Django', 'Flask', 'FastAPI', 'Java', 'Spring Boot', 'Hibernate', 'C++', 'C#', 
        'PHP', 'Laravel', 'Ruby', 'Ruby on Rails', 'JavaScript', 'TypeScript', 'React', 'Angular', 
        'Vue.js', 'Node.js', 'Express.js', 'Next.js', 'HTML5', 'CSS3', 'Bootstrap', 'Tailwind CSS', 
        'jQuery', 'ASP.NET', 'Swift', 'Kotlin', 'Flutter', 'React Native', 'Ionic', 'GraphQL', 'REST API',

        # --- DATA, AI & MACHINE LEARNING ---
        'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'NLP', 'Computer Vision', 
        'Data Science', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 
        'Tableau', 'PowerBI', 'R Programming', 'Data Visualization', 'Big Data', 'Hadoop', 'Spark', 
        'Kafka', 'Data Warehousing', 'ETL', 'Statistical Analysis', 'SAS', 'SPSS', 'MATLAB',

        # --- DATABASE & CYBERSECURITY ---
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'Oracle', 'Snowflake', 
        'Cybersecurity', 'Network Security', 'Firewalls', 'SIEM', 'Penetration Testing', 
        'Vulnerability Assessment', 'Ethical Hacking', 'Cryptography', 'Blockchain', 'Solidity',

        # --- SALES, MARKETING & BUSINESS ---
        'B2B Sales', 'B2C Sales', 'SaaS Sales', 'Lead Generation', 'CRM', 'Salesforce', 'HubSpot', 
        'Zoho', 'Cold Calling', 'Negotiation', 'Sales Strategy', 'Closing Deals', 'Account Management', 
        'Digital Marketing', 'SEO', 'SEM', 'Google Ads', 'Facebook Ads', 'Content Marketing', 
        'Email Marketing', 'Affiliate Marketing', 'Copywriting', 'Market Research', 'PPC',

        # --- MANAGEMENT, HR & OPERATIONS ---
        'Project Management', 'Agile', 'Scrum', 'Kanban', 'PMP', 'Prince2', 'Product Management', 
        'Operations Management', 'Supply Chain', 'Logistics', 'Procurement', 'Inventory Management', 
        'Human Resources', 'Talent Acquisition', 'Recruitment', 'Onboarding', 'Payroll', 'HRIS', 
        'Strategic Planning', 'Risk Management', 'Change Management', 'Vendor Management', 'Six Sigma',

        # --- FINANCE, BANKING & LEGAL ---
        'Accounting', 'Bookkeeping', 'Financial Analysis', 'Financial Modeling', 'Auditing', 
        'Taxation', 'Tally', 'QuickBooks', 'SAP', 'ERP', 'Budgeting', 'Compliance', 'Investment Banking', 
        'Wealth Management', 'Legal Research', 'Contract Negotiation', 'Intellectual Property',

        # --- CREATIVE, DESIGN & CONTENT ---
        'UI/UX Design', 'Product Design', 'Figma', 'Adobe XD', 'Sketch', 'Graphic Design', 
        'Adobe Photoshop', 'Illustrator', 'InDesign', 'Canva', 'Video Editing', 'Premiere Pro', 
        'After Effects', 'Copy Editing', 'Technical Writing', '3D Modeling', 'AutoCAD',

        # --- HEALTHCARE & REAL ESTATE ---
        'Clinical Research', 'Patient Care', 'Electronic Health Records', 'EHR', 'Medical Billing', 
        'Real Estate Sales', 'Property Management', 'Appraisal', 'Leasing', 'Interior Design',

        # --- UNIVERSAL SOFT SKILLS ---
        'Leadership', 'Team Building', 'Public Speaking', 'Conflict Resolution', 'Time Management', 
        'Problem Solving', 'Decision Making', 'Communication Skills', 'Customer Service', 
        'Technical Support', 'Multilingual', 'Crisis Management', 'Adaptability', 'Critical Thinking'
    ]
    
    found_skills = set()
    
    for skill in SKILL_DB:
        skill_lower = skill.lower()
        # Direct word matching [cite: 1]
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        if re.search(pattern, lemmatized_text):
            found_skills.add(skill)
        elif skill_lower in SYNONYM_MAP:
            # Check for synonyms if direct match fails [cite: 1]
            for synonym in SYNONYM_MAP[skill_lower]:
                syn_pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(syn_pattern, lemmatized_text):
                    found_skills.add(skill)
                    break
            
    unique_skills = sorted(list(found_skills))
    return ", ".join(unique_skills) if unique_skills else "No skills identified"