import os
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.utils.text import slugify
from django.utils import timezone
from django.http import HttpResponse

# Import your models, corrected form, and processing utils
from .models import RecruiterRoom, ResumeSubmission, Profile
from .forms import ExtendedUserCreationForm
from .utils import extract_text_from_pdf, calculate_match_score, extract_skills

# --- 1. Authentication & Registration ---

def landing_page(request):
    """Checks authentication and redirects to the correct workspace."""
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == 'RECRUITER':
                return redirect('dashboard')
            return redirect('home_ats_checker')
        except Profile.DoesNotExist:
            return render(request, 'screening/index.html', {'error': 'Profile missing. Please re-register.'})
    return render(request, 'screening/index.html')


def register(request):
    initial_role = request.GET.get('role', 'CANDIDATE').upper()

    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            # This call now handles both User and Profile role saving
            user = form.save() 
            
            login(request, user)
            # Redirect based on the profile role we just saved
            if user.profile.role == 'RECRUITER':
                return redirect('dashboard')
            return redirect('home_ats_checker')
    else:
        form = ExtendedUserCreationForm(initial={'role': initial_role})

    return render(request, 'registration/signup_unified.html', {'form': form})

class CustomLoginView(LoginView):
    """Handles role-based redirection after login."""
    template_name = 'registration/login.html' 

    def get_success_url(self):
        user = self.request.user
        # Safely checks for profile to prevent 'User has no profile' crashes
        if hasattr(user, 'profile'):
            if user.profile.role == 'RECRUITER':
                return reverse_lazy('dashboard')
            return reverse_lazy('home_ats_checker')
        return reverse_lazy('landing')


# --- 2. Candidate Workspace ---

@login_required
def home_ats_checker(request):
    """Direct ATS check for candidates (no room required)."""
    if request.user.profile.role == 'RECRUITER':
        return redirect('dashboard')
    
    score = None
    missing_skills = []
    
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        jd_text = request.POST.get('jd_text', '')
        
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        
        # Unpack match score and missing skills list
        score, missing_skills = calculate_match_score(raw_text, jd_text)
        
        default_storage.delete(path)
        
        return render(request, 'screening/home.html', {
            'score': score, 
            'missing_skills': missing_skills
        })
        
    return render(request, 'screening/home.html')


# screening/views.py

@login_required
def room_detail(request, slug):
    """Separates Recruiter (View applicants) from Candidate (Apply)."""
    room = get_object_or_404(RecruiterRoom, slug=slug)
    
    # 1. Handle Recruiters: Show them the applicant list
    if request.user.profile.role == 'RECRUITER':
        submissions = room.submissions.all().order_by('-score')
        return render(request, 'screening/room_admin.html', {
            'room': room, 
            'submissions': submissions
        })

    # 2. Handle Candidates: Show the Apply form
    if room.expires_at and timezone.now() > room.expires_at:
        return render(request, 'screening/room_closed.html', {'room': room})

    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        
        score, missing_skills_list = calculate_match_score(raw_text, room.jd_text)
        skills = extract_skills(raw_text)
        
        ResumeSubmission.objects.create(
            room=room,
            candidate=request.user,
            resume_file=uploaded_file,
            score=score,
            skills=skills
        )
        default_storage.delete(path)
        
        return render(request, 'screening/success.html', {
            'room': room,
            'score': score,
            'missing_skills': missing_skills_list
        })
        
    # This is the "Apply" page for candidates
    return render(request, 'screening/room_detail.html', {'room': room})

@login_required
def dashboard(request):
    """Displays all hiring rooms for the recruiter."""
    if request.user.profile.role == 'CANDIDATE':
        return redirect('home_ats_checker')
    
    # Staff see all rooms; regular recruiters see only their own
    if request.user.is_staff:
        rooms = RecruiterRoom.objects.all()
    else:
        rooms = RecruiterRoom.objects.filter(created_by=request.user)
        
    return render(request, 'screening/dashboard.html', {'rooms': rooms, 'now': timezone.now()})


@login_required
def create_room(request):
    """Creates a new hiring room with specific job requirements."""
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
    """Deletes a hiring room and all associated submissions."""
    room = get_object_or_404(RecruiterRoom, id=room_id, created_by=request.user)
    room.delete()
    return redirect('dashboard')


# --- 4. Analytics & Reports ---

@login_required
def compare_skills(request, submission_id):
    """Side-by-side comparison of candidate skills vs JD requirements."""
    submission = get_object_or_404(ResumeSubmission, id=submission_id)
    room = submission.room
    
    candidate_skills = set(submission.skills.split(", ")) if submission.skills else set()
    jd_skills = set(extract_skills(room.jd_text).split(", "))
    
    matched_skills = candidate_skills.intersection(jd_skills)
    missing_skills = jd_skills - candidate_skills
    extra_skills = candidate_skills - jd_skills

    # AI Insight Thresholds for the recruiter report
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
    """Exports selected candidate data to a professional Excel report."""
    if request.method == 'POST':
        ids = request.POST.getlist('selected_ids')
        submissions = ResumeSubmission.objects.filter(id__in=ids).order_by('-score')
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Candidate Analysis"
        ws.append(['Rank', 'Name', 'Email', 'ATS Score', 'Primary Skills', 'Applied Date'])
        
        for i, sub in enumerate(submissions, 1):
            ws.append([
                i, 
                sub.candidate.username, 
                sub.candidate.email, 
                f"{sub.score}%", 
                sub.skills, 
                sub.submitted_at.strftime('%Y-%m-%d')
            ])
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Candidate_Report.xlsx"'
        wb.save(response)
        return response
    return redirect('dashboard')