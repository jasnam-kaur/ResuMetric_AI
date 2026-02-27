from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_ROLES = (
        ('CANDIDATE', 'Candidate'),
        ('RECRUITER', 'Recruiter'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='CANDIDATE')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class RecruiterRoom(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    jd_text = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Add this model to fix the ImportError
class ResumeSubmission(models.Model):
    room = models.ForeignKey(RecruiterRoom, on_delete=models.CASCADE, related_name='submissions')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='submissions/')
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.room.name} ({self.score}%)"