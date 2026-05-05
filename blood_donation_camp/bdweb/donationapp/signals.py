# eventapp/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from donationapp.models import UserRole  # Only if you're still using a Role model (optional)

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == "donationapp":
        admin_email = "barshashreep05@gmail.com"
        admin_password = "pani@123"

        admin_user, created = User.objects.get_or_create(
            username=admin_email,
            defaults={
                "email": admin_email,
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            print("✅ Super admin created!")

        # Assign role only if not already assigned
        UserRole.objects.get_or_create(user=admin_user, role="admin")
