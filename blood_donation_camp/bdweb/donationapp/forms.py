from django import forms
from captcha.fields import CaptchaField
from django.contrib.auth.models import User
from .models import Donor,Recipient,DonationRequest,AdminProfile,HospitalClinic,HospitalBloodRequest

class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'})
    )
    captcha = CaptchaField()

class donorLoginForm(forms.Form):
    mobile = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Mobile No',
            'id': 'mobile'
        }),
        label='Enter Mobile No.'
    )
class recipientLoginForm(forms.Form):
    mobile = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Mobile No',
            'id': 'mobile'
        }),
        label='Enter Mobile No.'
    )
class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email ID',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email ID',
            'required': True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password',
            'required': True,
        })
    )    
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('donor', 'Donor'),
    ('recipient', 'Recipient'),
    ('clinic', 'Clinic'),
]


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

class donorregistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            "name", "email", "contact", "address", "aadhaar", "father_name", "age",
            "state", "district", "pin_code", "blood_group", "photo", "dob", "gender", "profession","role"
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "aadhaar": forms.TextInput(attrs={"class": "form-control"}),
            "father_name": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.NumberInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.TextInput(attrs={"class": "form-control"}),
            "pin_code": forms.TextInput(attrs={"class": "form-control"}),
            "blood_group": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "profession": forms.Select(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),  # new field
        }


class RecipientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['name', 'email', 'contact', 'address', 'id_proof', 'age', 'gender', 'state', 'district', 'pin_code','role']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'id_proof': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control'}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }
class AdminOTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label='OTP',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the OTP sent to your email',
        })
    )
    captcha = CaptchaField()
    


class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = [
            'name', 'age', 'blood_group', 'hospital_report',
            'weight', 'last_donation_date', 'requested_scheduleddate'
        ]
        widgets = {
            'requested_scheduleddate': forms.DateInput(attrs={'type': 'date'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
        }
from django import forms
from .models import RecipientRequest

class RecipientRequestForm(forms.ModelForm):
    class Meta:
        model = RecipientRequest
        exclude = ['recipient', 'status']
        widgets = {
            'blood_group': forms.Select(choices=[
                ('', 'Choose...'),
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
                ('O+', 'O+'), ('O-', 'O-'),
            ]),
        }



class AdminRegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=150, label='Full Name')
    email = forms.EmailField()
    contact = forms.CharField(max_length=15, label='Mobile Number')
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AdminProfile
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
# forms.py
from django import forms
from .models import BloodStock

class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ['blood_group', 'units', 'date_collected']
        widgets = {
            'date_collected': forms.DateInput(attrs={'type': 'date'})
        }
    
class HospitalClinicRegistrationForm(forms.ModelForm):
    class Meta:
        model = HospitalClinic
        fields = ['organization_name', 'related_blood_bank', 'state', 'district', 'pin_code',
                  'login_id', 'password', 'contact', 'location','role']
class HospitalLoginForm(forms.Form):
    login_id = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class HospitalOTPForm(forms.Form):
    otp = forms.CharField()
    captcha = CaptchaField()    
    


class HospitalBloodRequestForm(forms.ModelForm):
    class Meta:
        model = HospitalBloodRequest
        fields = ['organization_name', 'blood_group', 'units_required', 'purpose']
        widgets = {
            'blood_group': forms.Select(choices=[
                ('', 'Choose...'),
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
                ('O+', 'O+'), ('O-', 'O-'),
            ], attrs={'class': 'form-control'}),
            'units_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
