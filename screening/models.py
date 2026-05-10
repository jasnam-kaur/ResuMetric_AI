import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    USER_ROLES = [
        ('RECRUITER', 'Recruiter'),
        ('CANDIDATE', 'Candidate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class RecruiterRoom(models.Model):
    """
    Hiring Room with local AI overrides.
    Direct fields prevent FieldErrors in ModelForms.
    """
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    jd_text = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Matching Intelligence Fields (Now direct to support RoomEditForm)
    skill_weight = models.IntegerField(default=40)
    experience_weight = models.IntegerField(default=60)
    keyword_sensitivity = models.CharField(
        max_length=3, 
        choices=[('STR', 'Strict'), ('FLX', 'Flexible')], 
        default='FLX'
    )
    is_active = models.BooleanField(default=True)

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def get_weightage(self):
        """
        Returns the specific weights for this room.
        Used by execute_industry_screening.
        """
        return {
            "skill_weight": self.skill_weight,
            "experience_weight": self.experience_weight,
        }

    def __str__(self):
        return self.name


class ResumeSubmission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interviewing'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    ]
    room = models.ForeignKey(RecruiterRoom, on_delete=models.CASCADE, related_name='submissions')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='submissions/')
    score = models.FloatField()
    skills = models.TextField(default="No skills identified") 
    missing_skills = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    referral_code = models.UUIDField(default=uuid.uuid4, editable=False)
    is_premium_unlocked = models.BooleanField(default=False)
    referral_click_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Interview Scheduling
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_location = models.CharField(max_length=255, null=True, blank=True)
    interview_type = models.CharField(
        max_length=20, 
        choices=[('ONLINE', 'Online'), ('ON-SITE', 'On-Site')], 
        null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'candidate'], name='unique_candidate_submission_per_room')
        ]

    def __str__(self):
        return f"{self.candidate.username} - {self.room.slug} ({self.score}%)"


class GlobalSettings(models.Model):
    """
    System-wide default AI weights.
    Only one instance can be active at a time.
    """
    skill_weight = models.IntegerField(default=40)
    experience_weight = models.IntegerField(default=60)
    keyword_sensitivity = models.CharField(
        max_length=3, 
        choices=[('STR', 'Strict'), ('FLX', 'Flexible')], 
        default='FLX'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Global AI Setting"
        verbose_name_plural = "Global AI Settings"

    def save(self, *args, **kwargs):
        if self.is_active:
            # Singleton pattern: deactivate others
            GlobalSettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super(GlobalSettings, self).save(*args, **kwargs)

    def __str__(self):
        return f"Global Config (Active: {self.is_active})"