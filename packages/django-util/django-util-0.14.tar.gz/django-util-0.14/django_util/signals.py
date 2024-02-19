from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_util.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When User object is created, create Profile object
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
