from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from .utils import extract_text_from_pdf, clean_resume_text, calculate_match_score
import fitz
doc = fitz.open("resume.pdf")

def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        # Check if jd_text is actually in the POST data
        jd_text = request.POST.get('jd_text', '')
        
        if form.is_valid():
            resume_instance = form.save()
            
            # 1. Extract and Clean Text
            raw_text = extract_text_from_pdf(resume_instance.file.path)
            # Improved Name Extraction
            lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
            candidate_name = "Unknown Applicant"
            
            # Skip lines that look like addresses or labels
            for line in lines:
                if "address" not in line.lower() and ":" not in line:
                    candidate_name = line
                    break
            
            resume_instance.name = candidate_name

            cleaned_resume = clean_resume_text(raw_text)
            cleaned_jd = clean_resume_text(jd_text)
            
            # 2. DEBUG: Verify in terminal
            print(f"DEBUG: Resume Length: {len(cleaned_resume)}")
            print(f"DEBUG: JD Length: {len(cleaned_jd)}")
            
            # 3. Calculate Score (ONLY if both texts exist)
            if len(cleaned_resume) > 0 and len(cleaned_jd) > 0:
                score = calculate_match_score(cleaned_resume, cleaned_jd)
            else:
                score = 0.0
            
            # 4. Save the calculated score to the database
            resume_instance.score = score
            resume_instance.save()
            
            # 5. NOW return the success page with the updated instance
            return render(request, 'screening/success.html', {'resume': resume_instance})
    
    else:
        # This handles the initial page load (GET request)
        form = ResumeUploadForm()
    
    # This return handles showing the upload form if method is GET or if form is invalid
    return render(request, 'screening/upload.html', {'form': form})


def dashboard(request):
    # Retrieve all resumes from the database, highest score first
    resumes = Resume.objects.all().order_by('-score')
    return render(request, 'screening/dashboard.html', {'resumes': resumes})