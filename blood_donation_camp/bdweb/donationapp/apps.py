from django.apps import AppConfig


class DonationappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'donationapp'
    def ready(self):
        import donationapp.signals