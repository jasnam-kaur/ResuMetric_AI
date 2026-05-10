from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ResumeSubmission, GlobalSettings, RecruiterRoom

class ExtendedUserCreationForm(UserCreationForm):
    """
    Registration form that forces role selection.
    References Profile.USER_ROLES for consistency.
    """
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
        # Store the role temporarily on the user instance
        user._selected_role = self.cleaned_data.get('role')
        
        if commit:
            user.save()
            # Create the profile and link the selected role
            Profile.objects.update_or_create(
                user=user,
                defaults={'role': user._selected_role}
            )
        return user

class ResumeUploadForm(forms.ModelForm):
    """Standard form for candidate resume submission."""
    class Meta:
        model = ResumeSubmission 
        fields = ['resume_file']

class AlgorithmSettingsForm(forms.ModelForm):
    """
    Recruiter-only form to adjust AI Engine weights.
    Updated to use Integer weights (0-100) instead of Floats.
    """
    class Meta:
        model = GlobalSettings
        fields = ['skill_weight', 'experience_weight', 'keyword_sensitivity', 'is_active']
        widgets = {
            'skill_weight': forms.NumberInput(attrs={
                'type': 'range', 'step': '1', 'min': '0', 'max': '100', 'class': 'form-range'
            }),
            'experience_weight': forms.NumberInput(attrs={
                'type': 'range', 'step': '1', 'min': '0', 'max': '100', 'class': 'form-range'
            }),
            'keyword_sensitivity': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        skill = cleaned_data.get('skill_weight') or 0
        exp = cleaned_data.get('experience_weight') or 0
        
        # Validation updated for Integers: sum must be 100
        if skill + exp != 100:
            raise forms.ValidationError("The sum of Skill and Experience weights must equal exactly 100%.")
        return cleaned_data

class RoomEditForm(forms.ModelForm):
    """
    PROVISION: Allows Recruiters to edit room details and extend expiry.
    Updated field names to match GlobalSettings/RecruiterRoom models.
    """
    class Meta:
        model = RecruiterRoom
        # Use the exact field names defined in your RecruiterRoom model
        fields = ['skill_weight', 'experience_weight', 'keyword_sensitivity', 'is_active']
        widgets = {
            'skill_weight': forms.HiddenInput(),
            'experience_weight': forms.HiddenInput(),
            'keyword_sensitivity': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        skill = cleaned_data.get('skill_weight') or 0
        exp = cleaned_data.get('experience_weight') or 0
        
        if skill + exp != 100:
            raise forms.ValidationError("Total weight must equal 100%.")
        return cleaned_data