# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ExpertProfile, ClientProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.EXPERT:
            ExpertProfile.objects.create(user=instance)
        elif instance.role == User.Role.CLIENT:
            ClientProfile.objects.create(user=instance)
