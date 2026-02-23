# ResuMetric AI 🤖📄
**An Intelligent Resume Screening System using NLP and Machine Learning**

ResuMetric AI is a web-based Applicant Tracking System (ATS) developed as a Major Project for the BCA program. It goes beyond simple keyword matching by using Natural Language Processing (NLP) to rank resumes based on their actual content and relevance to a Job Description.

## 🚀 Key Features
* **AI-Powered Parsing:** Automatically extracts text and candidate names from PDF resumes using `PyMuPDF` and `spaCy`.
* **Vectorized Matching:** Uses `TF-IDF Vectorization` and `Cosine Similarity` to calculate an objective match percentage.
* **Recruiter Dashboard:** A real-time leaderboard that ranks candidates from highest to lowest score.
* **Cloud Ready:** Configured for seamless deployment on **Render** with WhiteNoise for static file management.

## 🛠️ Tech Stack
* **Backend:** Django (Python)
* **Machine Learning:** Scikit-Learn (TF-IDF, Cosine Similarity)
* **NLP:** spaCy (en_core_web_sm)
* **Database:** MySQL / SQLite
* **Frontend:** HTML5, Bootstrap 5

## 🔧 Installation & Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/jasnam-kaur/ResuMetric_AI.git](https://github.com/jasnam-kaur/ResuMetric_AI.git)