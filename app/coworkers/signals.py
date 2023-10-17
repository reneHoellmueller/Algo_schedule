from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print(f"Creating token for user {instance.username}")  # Hier prüfen, ob das Signal ausgelöst wird
        try:
            Token.objects.create(user=instance)
            print(f"Token created for user {instance.username}")  # Hier prüfen, ob der Token erfolgreich erstellt wurde
        except Exception as e:
            print(f"Failed to create token for user {instance.username}: {str(e)}")