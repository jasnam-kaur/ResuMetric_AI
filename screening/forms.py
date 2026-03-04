from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ResumeSubmission 

class ExtendedUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profile.USER_ROLES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select border-0 bg-transparent fw-bold text-primary shadow-none',
            'id': 'role_selection'
        })
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        
        user._selected_role = self.cleaned_data.get('role')
        
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={'role': user._selected_role}
            )
        return user

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeSubmission 
        fields = ['resume_file']