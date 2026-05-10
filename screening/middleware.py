from django.shortcuts import redirect
from django.urls import reverse
from .models import ResumeSubmission

class ResuMetricMiddleware:
    """
    Combined Middleware for:
    1. Referral Tracking (Unlocking Premium Features)
    2. Profile Completion Enforcement (Forcing Onboarding for both roles)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # --- LOGIC 1: REFERRAL TRACKING ---
        # This runs for everyone (even guest users) to track clicks
        ref_code = request.GET.get('ref')
        if ref_code:
            try:
                submission = ResumeSubmission.objects.get(referral_code=ref_code)
                submission.referral_click_count += 1
                submission.is_premium_unlocked = True 
                submission.save()
            except (ResumeSubmission.DoesNotExist, ValueError):
                pass 

        # --- LOGIC 2: PROFILE COMPLETION ENFORCEMENT ---
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            
            if profile and not profile.is_profile_complete:
                # Define common allowed paths (Logout is essential to prevent being trapped)
                allowed_paths = [reverse('logout')]
                target_setup_url = None

                # Role-based redirection logic
                if profile.role == 'CANDIDATE':
                    allowed_paths.append(reverse('profile_setup'))
                    target_setup_url = 'profile_setup'
                
                elif profile.role == 'RECRUITER':
                    allowed_paths.append(reverse('recruiter_setup'))
                    target_setup_url = 'recruiter_setup'

                # Execute redirect if not on an allowed path
                if target_setup_url:
                    is_on_allowed_path = request.path in allowed_paths
                    # Safety check: allow admin and media files to load
                    is_system_path = request.path.startswith('/admin/') or request.path.startswith('/media/') or request.path.startswith('/static/')
                    
                    if not is_on_allowed_path and not is_system_path:
                        return redirect(target_setup_url)

        # Final response execution (Everything else runs after this)
        response = self.get_response(request)
        return response