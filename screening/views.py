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
from django.contrib import messages

from .models import RecruiterRoom, ResumeSubmission, Profile
from .forms import ExtendedUserCreationForm
from .utils import extract_text_from_pdf, calculate_match_score, extract_skills


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
            user = form.save() 
            
            login(request, user)
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
        if hasattr(user, 'profile'):
            if user.profile.role == 'RECRUITER':
                return reverse_lazy('dashboard')
            return reverse_lazy('home_ats_checker')
        return reverse_lazy('landing')



@login_required
def home_ats_checker(request):
    """ATS check for candidates and Room-based application logic."""
    if request.user.profile.role == 'RECRUITER':
        return redirect('dashboard')
    
    score = None
    missing_skills = []
    
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        jd_text = request.POST.get('jd_text', '')
        room_code = request.POST.get('room_code')  # Get room code if available

        # 1. Logic for Room-Based Applications
        if room_code:
            try:
                room = RecruiterRoom.objects.get(slug=room_code)
                
                # Check if this candidate has already applied to this specific room
                already_applied = ResumeSubmission.objects.filter(
                    candidate=request.user, 
                    room=room
                ).exists()

                if already_applied:
                    messages.warning(request, f"You have already submitted an application to room {room_code}.")
                    return redirect('home_ats_checker')
                
            except RecruiterRoom.DoesNotExist:
                messages.error(request, "The hiring room code is invalid.")
                return redirect('home_ats_checker')

        # 2. Process the PDF
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        score, missing_skills = calculate_match_score(raw_text, jd_text)
        
        # 3. Save submission if it's for a room
        if room_code:
            ResumeSubmission.objects.create(
                candidate=request.user,
                room=room,
                resume_file=uploaded_file,
                score=score,
                skills=", ".join(missing_skills) 
            )
            messages.success(request, f"Application submitted successfully to room {room_code}!")

        default_storage.delete(path)
        
        return render(request, 'screening/home.html', {
            'score': score, 
            'missing_skills': missing_skills,
            'room_applied': room_code
        })
        
    return render(request, 'screening/home.html')

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib import messages # Import for user feedback

@login_required
def room_detail(request, slug):
    """Separates Recruiter (View applicants) from Candidate (Apply)."""
    
    try:
        room = RecruiterRoom.objects.get(slug=slug)
    except RecruiterRoom.DoesNotExist:
        return render(request, 'screening/room_not_found.html', {
            'attempted_code': slug
        })
    
    # 1. Recruiter View
    if request.user.profile.role == 'RECRUITER':
        submissions = room.submissions.all().order_by('-score')
        return render(request, 'screening/room_admin.html', {
            'room': room, 
            'submissions': submissions
        })

    # 2. Expiry Check
    if room.expires_at and timezone.now() > room.expires_at:
        return render(request, 'screening/room_closed.html', {'room': room})

    # 3. Handling POST Request
    if request.method == 'POST' and request.FILES.get('resume'):
        
        # 🛡️ PRE-SAVE CHECK: Prevent IntegrityError
        already_applied = ResumeSubmission.objects.filter(
            room=room, 
            candidate=request.user
        ).exists()

        if already_applied:
            messages.warning(request, f"You have already applied to {room.name}.")
            return redirect('room_detail', slug=slug)

        uploaded_file = request.FILES['resume']
        path = default_storage.save('temp/' + uploaded_file.name, uploaded_file)
        raw_text = extract_text_from_pdf(default_storage.path(path))
        
        score, missing_skills_list = calculate_match_score(raw_text, room.jd_text)
        skills = extract_skills(raw_text)
        
        # 🛡️ CREATE: This only fires if 'already_applied' is False
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