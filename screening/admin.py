from django.contrib import admin
from .models import Profile, RecruiterRoom, ResumeSubmission, GlobalSettings

# 1. Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'company_name', 'is_profile_complete')
    list_filter = ('role', 'is_profile_complete')
    search_fields = ('user__username', 'full_name', 'company_name')

# 2. Global AI Settings Admin (Fixed Duplicate Registration)
@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    """
    Differentiator: Administrative control over AI screening weights.
    Ensures recruiters can visually manage the 60/40 semantic split.
    """
    list_display = ('id', 'skill_weight', 'experience_weight', 'keyword_sensitivity', 'is_active')
    list_editable = ('is_active',)  # Allows quick toggling from the list view
    
    # Organize fields into sections for better UI
    fieldsets = (
        ('AI Weightage Configuration', {
            'fields': ('skill_weight', 'experience_weight')
        }),
        ('Algorithm Precision', {
            'fields': ('keyword_sensitivity', 'is_active')
        }),
    )

# 3. Recruiter Room Admin
@admin.register(RecruiterRoom)
class RecruiterRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'slug', 'expires_at', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# 4. Resume Submission Admin
@admin.register(ResumeSubmission)
class ResumeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'room', 'score', 'status', 'submitted_at')
    list_filter = ('status', 'room')
    search_fields = ('candidate__username', 'skills', 'missing_skills')
    readonly_fields = ('submitted_at',)
