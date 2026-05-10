"""
Blood Donation Camp Models
Includes models for Donors, Recipients, Hospitals, Camp Schedules, and Blood Stock management
"""

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from datetime import timedelta, date

# ============================================================================
# CHOICES AND CONSTANTS
# ============================================================================

class RoleChoices(models.TextChoices):
    """User role types in the system"""
    ADMIN = 'admin', 'Admin'
    DONOR = 'donor', 'Donor'
    RECIPIENT = 'recipient', 'Recipient'
    CLINIC = 'clinic', 'Clinic/Hospital'


class GenderChoices(models.TextChoices):
    """Gender options"""
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'
    OTHER = 'Other', 'Other'


class ProfessionChoices(models.TextChoices):
    """Profession/Employment status"""
    STUDENT = 'Student', 'Student'
    EMPLOYEE = 'Employee', 'Salaried Employee'
    SELF_EMPLOYED = 'Self-employed', 'Self-employed'
    OTHER = 'Other', 'Other'


class BloodGroupChoices(models.TextChoices):
    """Blood group types"""
    A_POSITIVE = 'A+', 'A+'
    A_NEGATIVE = 'A-', 'A-'
    B_POSITIVE = 'B+', 'B+'
    B_NEGATIVE = 'B-', 'B-'
    AB_POSITIVE = 'AB+', 'AB+'
    AB_NEGATIVE = 'AB-', 'AB-'
    O_POSITIVE = 'O+', 'O+'
    O_NEGATIVE = 'O-', 'O-'


class StatusChoices(models.TextChoices):
    """Request status options"""
    PENDING = 'Pending', 'Pending'
    ACCEPTED = 'Accepted', 'Accepted'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'


# ============================================================================
# VALIDATORS
# ============================================================================

mobile_validator = RegexValidator(
    regex=r'^\d{10,15}$',
    message='Mobile number must be 10-15 digits.'
)

aadhaar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message='Aadhaar number must be exactly 12 digits.'
)

pincode_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='Pin code must be exactly 6 digits.'
)


# ============================================================================
# MODELS
# ============================================================================

class UserRole(models.Model):
    """Maps Django User to Blood Donation System Roles"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blood_donation_role')
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "User Roles"
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.get_role_display()}"


class AdminProfile(models.Model):
    """Admin user profile with OTP support"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    mobile_number = models.CharField(
        max_length=15,
        validators=[mobile_validator],
        help_text="Contact mobile number for OTP verification"
    )
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Admin Profiles"

    def __str__(self) -> str:
        return f"Admin: {self.user.username}"

    def is_otp_valid(self) -> bool:
        """Check if OTP is still valid"""
        if not self.otp or not self.otp_expires_at:
            return False
        return timezone.now() < self.otp_expires_at


class Donor(models.Model):
    """Blood Donor Information"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15, validators=[mobile_validator])
    address = models.TextField()
    aadhaar = models.CharField(
        max_length=12,
        validators=[aadhaar_validator],
        unique=True
    )
    father_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(
        validators=[
            MinValueValidator(18, message="Donor must be at least 18 years old"),
            MaxValueValidator(65, message="Donor must be below 65 years old")
        ]
    )
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6, validators=[pincode_validator])
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    photo = models.ImageField(upload_to='donor_photos/')
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    profession = models.CharField(max_length=20, choices=ProfessionChoices.choices)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.DONOR
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Donors"
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['state', 'district']),
            models.Index(fields=['aadhaar']),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.blood_group}"

    def is_eligible_to_donate(self) -> bool:
        """Check if donor is eligible to donate"""
        if self.age < 18 or self.age > 65:
            return False
        return True


class DonationRequest(models.Model):
    """Blood donation request from a donor"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donation_requests')
    name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices, null=True)
    hospital_report = models.FileField(upload_to='hospital_reports/', null=True, blank=True)
    weight = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(45, message="Minimum weight required: 45 kg")]
    )
    last_donation_date = models.DateField(null=True, blank=True)
    requested_scheduleddate = models.DateField(null=True, blank=True)
    rejection_message = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Donation Requests"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['donor', 'status']),
        ]

    def __str__(self) -> str:
        return f"{self.name or self.donor.name} - {self.blood_group} - {self.get_status_display()}"

    def can_donate_again(self) -> bool:
        """Check if donor can donate again based on last donation date"""
        if not self.last_donation_date:
            return True
        days_since_donation = (date.today() - self.last_donation_date).days
        return days_since_donation >= 56  # Typical gap between donations


class Recipient(models.Model):
    """Blood Recipient Information"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15, validators=[mobile_validator])
    address = models.TextField()
    id_proof = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6, validators=[pincode_validator])
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.RECIPIENT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Recipients"
        indexes = [
            models.Index(fields=['state', 'district']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.age})"


class RecipientRequest(models.Model):
    """Blood request from recipient"""
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=100)
    patient_report = models.FileField(upload_to='patient_reports/')
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    units_required = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Minimum 1 unit required")]
    )
    address = models.TextField()
    id_proof = models.FileField(upload_to='recipient_id_proofs/')
    photo = models.ImageField(upload_to='recipient_photos/')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    requisition_form = models.FileField(upload_to='requisition_forms/', null=True, blank=True)
    admin_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Recipient Requests"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['blood_group']),
        ]

    def __str__(self) -> str:
        return f"{self.patient_name} - {self.blood_group} ({self.get_status_display()})"


class HospitalClinic(models.Model):
    """Hospital or Blood Bank/Clinic Information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    organization_name = models.CharField(max_length=100)
    related_blood_bank = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6, validators=[pincode_validator])
    login_id = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    contact = models.CharField(max_length=15, validators=[mobile_validator])
    location = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.CLINIC
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hospitals/Clinics"
        indexes = [
            models.Index(fields=['organization_name']),
            models.Index(fields=['state', 'district']),
        ]

    def __str__(self) -> str:
        return self.organization_name


class HospitalBloodRequest(models.Model):
    """Blood request from hospital/clinic"""
    hospital = models.ForeignKey(
        HospitalClinic,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )
    organization_name = models.CharField(max_length=100, null=True, blank=True)
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    units_required = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Minimum 1 unit required")]
    )
    purpose = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hospital Blood Requests"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['blood_group']),
        ]

    def __str__(self) -> str:
        org = self.organization_name or self.hospital.organization_name
        return f"{org} - {self.blood_group} ({self.units_required} units)"


class CampSchedule(models.Model):
    """Blood donation camp schedule"""
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Camp Schedules"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['state', 'district']),
        ]
        ordering = ['-date']

    def __str__(self) -> str:
        return f"{self.title} - {self.date}"

    def is_upcoming(self) -> bool:
        """Check if camp is in the future"""
        return date.today() <= self.date


class OTP(models.Model):
    """One-Time Password for user authentication"""
    mobile_number = models.CharField(max_length=15, validators=[mobile_validator])
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        indexes = [
            models.Index(fields=['mobile_number']),
        ]

    def __str__(self) -> str:
        return f"OTP for {self.mobile_number}"

    def is_valid(self) -> bool:
        """Check if OTP is still valid (5 minutes)"""
        time_diff = timezone.now() - self.created_at
        return time_diff.total_seconds() < 300


class AdminOTP(models.Model):
    """One-Time Password for Admin authentication"""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Admin OTP"
        verbose_name_plural = "Admin OTPs"
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self) -> str:
        return f"OTP for {self.email}"

    def is_valid(self) -> bool:
        """Check if OTP is still valid (5 minutes)"""
        return timezone.now() < self.created_at + timedelta(minutes=5)


class BloodStock(models.Model):
    """Blood inventory management"""
    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    units = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    date_collected = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Blood Stock"
        indexes = [
            models.Index(fields=['blood_group']),
            models.Index(fields=['date_collected']),
        ]
        unique_together = ['blood_group', 'date_collected']

    def __str__(self) -> str:
        return f"{self.blood_group} - {self.units} units (Collected: {self.date_collected})"

    @property
    def expiry_date(self) -> date:
        """Blood expires 42 days after collection"""
        return self.date_collected + timedelta(days=42)

    def is_expired(self) -> bool:
        """Check if blood stock has expired"""
        return date.today() > self.expiry_date

    def days_until_expiry(self) -> int:
        """Calculate days remaining before expiry"""
        days = (self.expiry_date - date.today()).days
        return max(0, days)
