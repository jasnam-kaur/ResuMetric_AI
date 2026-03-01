import os
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.utils.text import slugify
from django.utils import timezone
from django.http import HttpResponse

# Import your models and processing utils
from .models import RecruiterRoom, ResumeSubmission
from .utils import extract_text_from_pdf, calculate_match_score, extract_skills

# --- 1. Authentication & Registration ---

def landing_page(request):
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'RECRUITER':
                return redirect('dashboard')
            return redirect('home_ats_checker')
        except Profile.DoesNotExist:
            # If profile is missing, create a default one or logout
            return render(request, 'screening/index.html', {'error': 'Profile missing. Please re-register.'})
    return render(request, 'screening/index.html')

from .models import Profile # Ensure this is imported
# screening/views.py

# screening/views.py
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role', 'CANDIDATE') 
        
        if form.is_valid():
            user = form.save()
            # Safety: Get or create the profile to prevent RelatedObjectDoesNotExist
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            
            login(request, user)
            return redirect('dashboard' if role == 'RECRUITER' else 'home_ats_checker')
        
        # If form is invalid, stay on the signup page (Fixes ValueError)
        return render(request, 'registration/signup_unified.html', {'form': form})

    # GET request: Show the unified signup form
    form = UserCreationForm()
    return render(request, 'registration/signup_unified.html', {'form': form})

class CustomLoginView(LoginView):
    # Updated to the single file you kept
    template_name = 'registration/login.html' 

    def get_success_url(self):
        user = self.request.user
        # Safely checks for profile to prevent the 'User has no profile' crash
        if hasattr(user, 'profile'):
            if user.profile.role == 'CANDIDATE':
                return reverse_lazy('home_ats_checker')
            elif user.profile.role == 'RECRUITER':
                return reverse_lazy('dashboard')
        return reverse_lazy('landing')

# --- 2. Candidate Workspace ---

@login_required
def home_ats_checker(request):
    if request.user.profile.role == 'RECRUITER':
        return redirect('dashboard')
    score = None
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        jd_text = request.POST.get('jd_text', '')
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        score = calculate_match_score(raw_text, jd_text)
        default_storage.delete(path)
        return render(request, 'screening/home.html', {'score': score})
    return render(request, 'screening/home.html')

@login_required
def room_detail(request, slug):
    room = get_object_or_404(RecruiterRoom, slug=slug)
    
    # Check if room is expired
    if room.expires_at and timezone.now() > room.expires_at:
        return render(request, 'screening/room_closed.html', {'room': room})

    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        
        # Core Processing Features
        score = calculate_match_score(raw_text, room.jd_text)
        skills = extract_skills(raw_text)
        
        # Save submission
        ResumeSubmission.objects.create(
            room=room,
            candidate=request.user,
            resume_file=uploaded_file,
            score=score,
            skills=skills
        )
        default_storage.delete(path)
        return render(request, 'screening/success.html', {'room': room})
    return render(request, 'screening/room_detail.html', {'room': room})

# --- 3. Recruiter Workspace ---

@login_required
def dashboard(request):
    if request.user.profile.role == 'CANDIDATE':
        return redirect('home_ats_checker')
    rooms = RecruiterRoom.objects.all() if request.user.is_staff else RecruiterRoom.objects.filter(created_by=request.user)
    return render(request, 'screening/dashboard.html', {'rooms': rooms, 'now': timezone.now()})

@login_required
def create_room(request):
    if request.user.profile.role == 'CANDIDATE':
        return redirect('home_ats_checker')
    if request.method == 'POST':
        name = request.POST.get('name')
        RecruiterRoom.objects.create(
            created_by=request.user,
            name=name,
            slug=slugify(name),
            jd_text=request.POST.get('jd_text'),
            expires_at=request.POST.get('expires_at') or None
        )
        return redirect('dashboard')
    return render(request, 'screening/create_room.html')

@login_required
def delete_room(request, room_id):
    room = get_object_or_404(RecruiterRoom, id=room_id, created_by=request.user)
    room.delete()
    return redirect('dashboard')

# --- 4. Analytics & Reports ---

@login_required
def compare_skills(request, submission_id):
    submission = get_object_or_404(ResumeSubmission, id=submission_id)
    room = submission.room
    candidate_skills = set(submission.skills.split(", ")) if submission.skills else set()
    jd_skills = set(extract_skills(room.jd_text).split(", "))
    
    # Analysis Logic
    matched_skills = candidate_skills.intersection(jd_skills)
    missing_skills = jd_skills - candidate_skills
    extra_skills = candidate_skills - jd_skills

    # AI Insights Logic
    if submission.score >= 80:
        insight = "Strong Match: Candidate possesses most core technical requirements."
    elif submission.score >= 50:
        insight = "Potential Match: Good foundation, but some skill gaps identified."
    else:
        insight = "Weak Match: Missing significant core requirements for this role."

    context = {
        'submission': submission,
        'room': room,
        'matched_skills': sorted(list(matched_skills)),
        'missing_skills': sorted(list(missing_skills)),
        'extra_skills': sorted(list(extra_skills)),
        'ai_insight': insight
    }
    return render(request, 'screening/compare_skills.html', context)

@login_required
def export_to_excel(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_ids')
        submissions = ResumeSubmission.objects.filter(id__in=ids).order_by('-score')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Candidate Analysis"
        ws.append(['Rank', 'Name', 'Email', 'ATS Score', 'Primary Skills', 'Applied Date'])
        for i, sub in enumerate(submissions, 1):
            ws.append([i, sub.candidate.username, sub.candidate.email, f"{sub.score}%", sub.skills, sub.submitted_at.strftime('%Y-%m-%d')])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Candidate_Report.xlsx"'
        wb.save(response)
        return response
    return redirect('dashboard')