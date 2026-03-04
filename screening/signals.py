from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if a specific role was intended during registration
        # This allows the form/view to 'hint' the correct role to the signal
        role = getattr(instance, '_selected_role', 'CANDIDATE')
        Profile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        # Ensure profile exists and is saved on user updates
        if hasattr(instance, 'profile'):
            instance.profile.save()