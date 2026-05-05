from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User

# ROLE CHOICES
ROLE_CHOICES = (
    ('donor', 'Donor'),
    ('recipient', 'Recipient'),
    ('clinic', 'Clinic'),
    ('admin', 'Admin'),
)

# User role mapping
class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Admin Profile
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username

# Donor Model
# --- Place these at the top of your models.py ---
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('donor', 'Donor'),
    ('recipient', 'Recipient'),
    ('clinic', 'Clinic'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

PROFESSION_CHOICES = [
    ('Student', 'Student'),
    ('Employee', 'Employee'),
    ('Self-employed', 'Self-employed'),
    ('Other', 'Other'),
]

BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
]

class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    address = models.TextField()
    aadhaar = models.CharField(max_length=12)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    photo = models.ImageField(upload_to='donor_photos/')
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,default='None')  # ✅ Add this
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES,default='None')  # ✅ Add this
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')



class DonationRequest(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True)
    age = models.IntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=5,null=True)
    hospital_report = models.FileField(upload_to='hospital_reports/',null=True)
    weight = models.FloatField(null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    requested_scheduleddate = models.DateField(null=True, blank=True)
    
    rejection_message = models.TextField(null=True, blank=True) 
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.name} - {self.blood_group} - {self.status}"

# Recipient Model
class Recipient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    address = models.TextField()
    id_proof = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ])
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6) 
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recipient')# ✅ should be pin_code


# Recipient Blood Request
class RecipientRequest(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    patient_report = models.FileField(upload_to='patient_reports/')
    blood_group = models.CharField(max_length=5)
    units_required = models.PositiveIntegerField()
    address = models.TextField()
    id_proof = models.FileField(upload_to='recipient_id_proofs/')
    photo = models.ImageField(upload_to='recipient_photos/')
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    requisition_form = models.FileField(upload_to='requisition_forms/', null=True, blank=True)  
    admin_message = models.TextField(null=True, blank=True)
    
# Hospital/Clinic
class HospitalClinic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Added user link
    organization_name = models.CharField(max_length=100)
    related_blood_bank = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    login_id = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)  # For OTP
    location = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='hospital')

    def __str__(self):
        return self.organization_name



class HospitalBloodRequest(models.Model):
    hospital = models.ForeignKey(HospitalClinic, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=100,null=True)  
    blood_group = models.CharField(max_length=5)
    units_required = models.PositiveIntegerField()
    purpose = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )



# Camp Schedule
class CampSchedule(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    state = models.CharField(max_length=100, null=True)
    district = models.CharField(max_length=100, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

# General OTP (for Donor, Recipient, Clinic)
class OTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 minutes

# Admin OTP
class AdminOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + datetime.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"
# models.py
from django.db import models
from datetime import timedelta, date

BLOOD_GROUPS = [
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
]

class BloodStock(models.Model):
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units = models.PositiveIntegerField(blank=True, null=True)
    date_collected = models.DateField(blank=True, null=True)

    @property
    def expiry_date(self):
        return self.date_collected + timedelta(days=42)  # Typical shelf life of 42 days

    def is_expired(self):
        return date.today() > self.expiry_date

    def __str__(self):
        return f"{self.blood_group} - {self.units} units"
