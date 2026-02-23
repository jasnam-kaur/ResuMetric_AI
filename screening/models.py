from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0)  # This is where the AI score will go
    skills = models.TextField(blank=True)   # Extracted skills from AI

    def __str__(self):
        return self.name if self.name else f"Resume {self.id}"