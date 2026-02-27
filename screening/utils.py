import fitz  # Standard for PyMuPDF 1.23.22
import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy for Lemmatization
# Make sure to run: python -m spacy download en_core_web_sm
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
    if not resume_text or not jd_text:
        return 0.0
    
    clean_resume = clean_resume_text(resume_text)
    clean_jd = clean_resume_text(jd_text)
    
    # 1. Base TF-IDF Similarity (Global context)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
    base_similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]) * 100

    # 2. Hard Skill Matcher (Weighted Bonus)
    # Extract sets of skills from both
    resume_skills = set(extract_skills(resume_text).split(", "))
    jd_skills = set(extract_skills(jd_text).split(", "))
    
    if not jd_skills:
        return round(base_similarity, 2)

    # Calculate what percentage of JD skills are present
    matched_skills = resume_skills.intersection(jd_skills)
    skill_match_ratio = len(matched_skills) / len(jd_skills)
    
    # 3. Final Weighted Formula
    # 60% weight to TF-IDF (Overall context)
    # 40% weight to Hard Skill Match (Precision)
    final_score = (base_similarity * 0.6) + (skill_match_ratio * 100 * 0.4)
    
    return round(min(final_score, 100.0), 2)

def extract_skills(text):
    """
    Checklist Item: Dynamic Skill Extraction
    Uses Lemmatization to match resume text against the Global Skill DB.
    """
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
    
    # Step 1: Lemmatize the resume text to catch root words
    lemmatized_text = clean_resume_text(text)
    
    found_skills = []
    
    # Step 2: Match against the database
    for skill in SKILL_DB:
        # Regex \b ensures whole word matching
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, lemmatized_text):
            found_skills.append(skill)
            
    unique_skills = sorted(list(set(found_skills)))
    return ", ".join(unique_skills) if unique_skills else "No skills identified"