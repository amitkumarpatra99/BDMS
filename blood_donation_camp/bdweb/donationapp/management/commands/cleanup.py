"""
Management command to cleanup expired OTPs and blood stock
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from donationapp.models import OTP, AdminOTP, BloodStock

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleanup expired OTPs and blood stock'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING('🧹 Starting cleanup...'))
        
        # Cleanup expired OTPs
        cutoff_time = timezone.now() - timedelta(hours=1)
        expired_otps = OTP.objects.filter(created_at__lt=cutoff_time)
        otp_count = expired_otps.count()
        
        if dry_run:
            self.stdout.write(f"Would delete {otp_count} expired OTPs")
        else:
            expired_otps.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {otp_count} expired OTPs')
            )
            logger.info(f"Cleanup: Deleted {otp_count} expired OTPs")
        
        # Cleanup expired Admin OTPs
        expired_admin_otps = AdminOTP.objects.filter(created_at__lt=cutoff_time)
        admin_otp_count = expired_admin_otps.count()
        
        if dry_run:
            self.stdout.write(f"Would delete {admin_otp_count} expired admin OTPs")
        else:
            expired_admin_otps.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {admin_otp_count} expired admin OTPs')
            )
            logger.info(f"Cleanup: Deleted {admin_otp_count} expired admin OTPs")
        
        # Mark expired blood stock
        import datetime
        cutoff_date = datetime.date.today() - timedelta(days=42)
        expired_blood = BloodStock.objects.filter(date_collected__lt=cutoff_date)
        blood_count = expired_blood.count()
        
        if dry_run:
            self.stdout.write(f"Would mark {blood_count} blood units as expired")
        else:
            expired_blood.update(units=0)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Marked {blood_count} expired blood units')
            )
            logger.info(f"Cleanup: Marked {blood_count} blood units as expired")
        
        self.stdout.write(self.style.SUCCESS('🎉 Cleanup completed!'))
