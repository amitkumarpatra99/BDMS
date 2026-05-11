# eventapp/signals.py
import os
import logging
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from donationapp.models import UserRole

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == "donationapp":
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@yourdomain.com')
        admin_password = os.environ.get('ADMIN_PASSWORD')

        if not admin_password:
            logger.warning(
                'ADMIN_PASSWORD is not configured. Default superuser creation skipped for %s.',
                admin_email
            )
            return

        admin_user, created = User.objects.get_or_create(
            username=admin_email,
            defaults={
                'email': admin_email,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            logger.info('Super admin account created for %s', admin_email)

        UserRole.objects.get_or_create(user=admin_user, role='admin')
