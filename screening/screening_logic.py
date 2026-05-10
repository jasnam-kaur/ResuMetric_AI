import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import GlobalSettings

# Load spaCy for advanced NLP lemmatization
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

SYNONYM_MAP = {
    # --- WEB & APP DEVELOPMENT (Global Standards) ---
    'django': ['web framework', 'python backend', 'mvc', 'drf', 'django rest framework', 'fullstack python'],
    'react': ['frontend', 'javascript library', 'spa', 'web development', 'react.js', 'reactjs', 'ui library'],
    'flutter': ['cross-platform mobile', 'dart programming', 'mobile ui', 'app development'],
    'next.js': ['ssr', 'static site generation', 'server-side rendering', 'vercel stack'],
    
    # --- CLOUD, DEVOPS & SRE ---
    'docker': ['containerization', 'devops', 'kubernetes', 'containers', 'oci', 'image registry'],
    'kubernetes': ['k8s', 'orchestration', 'container management', 'helm', 'eks', 'gke', 'aks', 'openshift'],
    'aws': ['cloud computing', 'amazon web services', 'cloud infrastructure', 'ec2', 's3', 'serverless', 'lambda', 'iam'],
    'azure': ['microsoft cloud', 'azure devops', 'cloud architect', 'active directory', 'blob storage'],
    'terraform': ['iac', 'infrastructure as code', 'cloud automation', 'hcl', 'cloudformation'],
    'jenkins': ['ci/cd', 'continuous integration', 'automation server', 'pipelines', 'github actions', 'gitlab ci'],
    'sre': ['site reliability engineering', 'system availability', 'infrastructure monitoring', 'uptime'],

    # --- DATABASES & BIG DATA ---
    'postgresql': ['sql', 'relational database', 'postgres', 'dbms', 'rdbms', 'transactional data'],
    'mongodb': ['nosql', 'document store', 'json database', 'non-relational', 'atlas'],
    'snowflake': ['data warehouse', 'cloud data platform', 'olap', 'big data storage'],
    'kafka': ['event streaming', 'message broker', 'pub/sub', 'real-time data', 'confluent'],
    'hadoop': ['distributed computing', 'mapreduce', 'hdfs', 'big data ecosystem'],

    # --- AI, GEN-AI & DATA SCIENCE ---
    'scikit-learn': ['machine learning', 'data science', 'ai', 'predictive modeling', 'sklearn', 'regression'],
    'tensorflow': ['deep learning', 'neural networks', 'ai', 'keras', 'ml', 'computer vision'],
    'pytorch': ['deep learning', 'ai', 'torch', 'computer vision', 'fast.ai'],
    'nlp': ['natural language processing', 'text analysis', 'computational linguistics', 'llm', 'bert', 'transformers'],
    'langchain': ['llm orchestration', 'generative ai', 'prompt engineering', 'ai agents', 'rag'],
    'openai': ['gpt', 'llm', 'generative ai', 'chatgpt api', 'dall-e'],

    # --- FINTECH & BLOCKCHAIN ---
    'blockchain': ['distributed ledger', 'web3', 'defi', 'dlt'],
    'ethereum': ['solidity', 'smart contracts', 'erc-20', 'evm'],
    'fintech': ['digital banking', 'payment gateways', 'open banking', 'trading platforms'],
    'compliance': ['aml', 'kyc', 'regulatory reporting', 'gdpr', 'sox'],

    # --- HEALTHTECH & BIOTECH ---
    'clinical research': ['clinical trials', 'ich-gcp', 'pharma research', 'cro'],
    'ehr': ['electronic health records', 'emr', 'health informatics', 'hl7', 'fhir'],
    'biotechnology': ['genomics', 'molecular biology', 'bioinformatics', 'lab automation'],

    # --- INDUSTRIAL, RENEWABLES & LOGISTICS ---
    'supply chain': ['logistics', 'scm', 'inventory control', 'procurement', 'last mile'],
    'renewable energy': ['solar energy', 'wind power', 'clean tech', 'sustainability', 'esg'],
    'industry 4.0': ['iiot', 'industrial internet of things', 'smart manufacturing', 'plc', 'scada'],

    # --- HUMAN RESOURCES & HRIS ---
    'hris': ['bamboohr', 'workday', 'hr database', 'peoplesoft', 'hippo', 'successfactors'],
    'ats': ['recruitment software', 'applicant tracking system', 'lever', 'greenhouse', 'smartrecruiters'],
    'recruitment': ['hiring', 'talent acquisition', 'sourcing', 'headhunting', 'executive search'],
}

SKILL_DB = [
    # --- CLOUD & INFRASTRUCTURE ---
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible', 'Puppet', 
    'Chef', 'Cloud Computing', 'CI/CD', 'Linux', 'Unix', 'Bash', 'Shell Scripting', 'Virtualization', 
    'VMware', 'OpenStack', 'DevOps', 'SRE', 'JMeter', 'Nagios', 'Prometheus', 'Grafana', 
    'Microservices', 'Serverless', 'Lambda', 'EC2', 'S3', 'CloudFront', 'Route53', 'Nginx',

    # --- SOFTWARE & LANGUAGES ---
    'Python', 'Django', 'Flask', 'FastAPI', 'Java', 'Spring Boot', 'Hibernate', 'C++', 'C#', 
    'PHP', 'Laravel', 'Ruby', 'Ruby on Rails', 'JavaScript', 'TypeScript', 'React', 'Angular', 
    'Vue.js', 'Node.js', 'Express.js', 'Next.js', 'HTML5', 'CSS3', 'Bootstrap', 'Tailwind CSS', 
    'jQuery', 'ASP.NET', 'Swift', 'Kotlin', 'Flutter', 'React Native', 'Ionic', 'GraphQL', 'REST API',
    'Rust', 'Go', 'Mojo', 'Scala', 'Perl', 'Solidity', 'Dart',

    # --- AI, ML & DATA ---
    'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'NLP', 'Computer Vision', 
    'Data Science', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 
    'Tableau', 'PowerBI', 'R Programming', 'Data Visualization', 'Big Data', 'Hadoop', 'Spark', 
    'Kafka', 'Data Warehousing', 'ETL', 'Statistical Analysis', 'SAS', 'SPSS', 'MATLAB',
    'Prompt Engineering', 'Generative AI', 'LLM', 'LangChain', 'Vector Databases', 'Hugging Face',

    # --- FINTECH, SECURITY & BLOCKCHAIN ---
    'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra', 'Oracle', 'Snowflake', 
    'Cybersecurity', 'Network Security', 'Firewalls', 'SIEM', 'Penetration Testing', 
    'Vulnerability Assessment', 'Ethical Hacking', 'Cryptography', 'Blockchain', 'Solana', 
    'Ethereum', 'Smart Contracts', 'DeFi', 'AML/KYC', 'Quantitative Analysis',

    # --- HEALTHTECH & PHARMA ---
    'Clinical Research', 'EHR', 'Bioinformatics', 'Genomics', 'Medical Imaging', 'HIPAA Compliance',
    'HL7', 'FHIR', 'Pharmacovigilance', 'Telemedicine',

    # --- ENGINEERING & MANUFACTURING ---
    'AutoCAD', 'SolidWorks', 'MATLAB', 'PLC Programming', 'SCADA', 'IIoT', 'Six Sigma', 
    'Lean Manufacturing', 'Robotics', 'Structural Engineering', 'Mechanical Engineering',

    # --- HR, SALES & BUSINESS ---
    'Project Management', 'Agile', 'Scrum', 'Kanban', 'PMP', 'Prince2', 'Product Management', 
    'Supply Chain', 'Logistics', 'Human Resources', 'Talent Acquisition', 'Recruitment', 
    'Payroll', 'HRIS', 'CRM', 'Salesforce', 'HubSpot', 'B2B Sales', 'Digital Marketing', 
    'SEO', 'ESG Reporting', 'Sustainability Strategy',

    # --- UNIVERSAL SOFT SKILLS ---
    'Leadership', 'Team Building', 'Public Speaking', 'Conflict Resolution', 'Time Management', 
    'Problem Solving', 'Communication Skills', 'Customer Service', 'Technical Support', 
    'Critical Thinking', 'Adaptability', 'Emotional Intelligence'
]

# --- HELPER FUNCTIONS ---

def clean_resume_text(text):
    """
    Advanced cleaning using NLP Lemmatization.
    Fixes the 'Python(Basics)' issue by replacing parentheses with spaces.
    """
    if not text: return ""
    text = text.lower()
    # CRITICAL FIX: Ensure 'Python(Basics)' becomes 'python basics'
    text = text.replace('(', ' ').replace(')', ' ')
    # Process text through spaCy
    doc = nlp(text)
    # Lemmatize and remove stop words/punctuation
    lemmatized = " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])
    return lemmatized.strip()

def extract_hard_skills(text, settings=None):
    """
    Matches text against the Global Skill DB using lemmatization and synonyms.
    """
    lemmatized_text = clean_resume_text(text)
    found_skills = set()
    
    for skill in SKILL_DB:
        skill_lower = skill.lower()
        # Use regex boundaries for accuracy
        pattern = rf'\b{re.escape(skill_lower)}\b'
        
        if re.search(pattern, lemmatized_text):
            found_skills.add(skill)
        elif skill_lower in SYNONYM_MAP:
            for synonym in SYNONYM_MAP[skill_lower]:
                syn_pattern = rf'\b{re.escape(synonym)}\b'
                if re.search(syn_pattern, lemmatized_text):
                    found_skills.add(skill)
                    break
                    
    return found_skills

# --- CORE SCREENING ENGINE ---

def execute_industry_screening(resume_text, jd_text, weights=None):
    """Safely handles weights to prevent GlobalSettings attribute errors."""
    if not resume_text or not jd_text:
        return {'score': 0.0, 'matched': [], 'missing': []}

    # 1. Resilient Weight Initialization
    if not weights:
        settings = GlobalSettings.objects.filter(is_active=True).first()
        # Use getattr to provide hardcoded fallbacks if the attributes are missing
        weights = {
            'skill_weight': getattr(settings, 'skill_weight', 40), 
            'experience_weight': getattr(settings, 'experience_weight', 60)
        }
    """
    AI Screening Engine: Combines TF-IDF Context Match (Semantic) 
    with Hard Skill Accuracy (Keyword).
    """
    if not resume_text or not jd_text:
        return {'score': 0.0, 'matched': [], 'missing': []}

    # 1. Initialize Weights (Dynamic Room-Specific vs Global)
    if not weights:
        settings = GlobalSettings.objects.filter(is_active=True).first()
        weights = {
            'skill_weight': settings.skill_weight if settings else 60,
            'experience_weight': settings.experience_weight if settings else 40
        }

    # 2. Pre-processing
    clean_resume = clean_resume_text(resume_text)
    clean_jd = clean_resume_text(jd_text)

    # 3. Hard Skill Extraction
    resume_skills = extract_hard_skills(resume_text) 
    jd_skills = extract_hard_skills(jd_text)
    
    matched_set = resume_skills.intersection(jd_skills)
    missing_set = jd_skills.difference(resume_skills)
    
    # 4. Component Scoring
    # A. Hard Skill Matcher (Usually 40% weight)
    skill_match_ratio = (len(matched_set) / len(jd_skills)) * 100 if jd_skills else 0.0
    
    # B. TF-IDF Semantic Similarity (Usually 60% weight)
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        base_similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]) * 100
    except:
        base_similarity = 0.0

    # 5. Final Calculation based on Room-Specific Sliders
    s_multiplier = weights.get('skill_weight', 60) / 100
    e_multiplier = weights.get('experience_weight', 40) / 100

    final_score = (base_similarity * e_multiplier) + (skill_match_ratio * s_multiplier)

    return {
        'score': round(min(final_score, 100.0), 2),
        'matched': sorted(list(matched_set)),
        'missing': sorted(list(missing_set)) if jd_skills else ["ADD KEYWORDS TO JD"]
    }

