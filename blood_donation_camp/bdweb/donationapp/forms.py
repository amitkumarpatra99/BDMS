"""
Django forms for Blood Donation Camp application
Includes validation for all user inputs
"""

import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

from .models import (
    Donor, Recipient, DonationRequest, AdminProfile,
    HospitalClinic, HospitalBloodRequest, BloodStock,
    RecipientRequest, RoleChoices, GenderChoices,
    ProfessionChoices, BloodGroupChoices
)


# ============================================================================
# CUSTOM VALIDATORS
# ============================================================================

class MobileNumberValidator:
    """Validator for mobile numbers"""
    
    def __call__(self, value):
        # Remove any non-digit characters
        cleaned = re.sub(r'\D', '', value)
        
        if len(cleaned) < 10:
            raise ValidationError('Mobile number must have at least 10 digits')
        if len(cleaned) > 15:
            raise ValidationError('Mobile number cannot exceed 15 digits')


class AadhaarValidator:
    """Validator for Aadhaar numbers"""
    
    def __call__(self, value):
        # Aadhaar must be 12 digits
        if not re.match(r'^\d{12}$', value):
            raise ValidationError('Aadhaar number must be exactly 12 digits')


class PincodeValidator:
    """Validator for pincode"""
    
    def __call__(self, value):
        if not re.match(r'^\d{6}$', value):
            raise ValidationError('Pincode must be exactly 6 digits')


# ============================================================================
# AUTHENTICATION FORMS
# ============================================================================

class DonorLoginForm(forms.Form):
    """Form for donor login"""
    mobile = forms.CharField(
        max_length=15,
        label='Mobile Number',
        validators=[MobileNumberValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 10-digit mobile number',
            'id': 'mobile',
            'autocomplete': 'tel',
        })
    )
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            # Normalize mobile number
            cleaned_mobile = re.sub(r'\D', '', mobile)
            return cleaned_mobile
        return mobile


class RecipientLoginForm(forms.Form):
    """Form for recipient login"""
    mobile = forms.CharField(
        max_length=15,
        label='Mobile Number',
        validators=[MobileNumberValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 10-digit mobile number',
            'id': 'mobile',
            'autocomplete': 'tel',
        })
    )
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile:
            cleaned_mobile = re.sub(r'\D', '', mobile)
            return cleaned_mobile
        return mobile


class AdminLoginForm(forms.Form):
    """Form for admin login"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
        })
    )


class OTPForm(forms.Form):
    """Form for OTP verification"""
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label='One-Time Password',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
        })
    )
    captcha = CaptchaField(label='')
    
    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if otp and not otp.isdigit():
            raise ValidationError('OTP must contain only digits')
        return otp


class AdminOTPVerificationForm(forms.Form):
    """Form for admin OTP verification"""
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label='One-Time Password',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'inputmode': 'numeric',
        })
    )
    captcha = CaptchaField(label='')


class HospitalLoginForm(forms.Form):
    """Form for hospital login"""
    login_id = forms.CharField(
        max_length=100,
        label='Login ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter hospital login ID',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )


class HospitalOTPForm(forms.Form):
    """Form for hospital OTP verification"""
    otp = forms.CharField(
        max_length=6,
        label='One-Time Password',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter OTP sent to your email/phone',
        })
    )
    captcha = CaptchaField(label='')


# ============================================================================
# DONOR FORMS
# ============================================================================

class DonorRegistrationForm(forms.ModelForm):
    """Form for donor registration"""
    confirm_password = forms.CharField(
        label='Confirm Password (optional)',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Donor
        fields = [
            'name', 'email', 'contact', 'address', 'aadhaar',
            'father_name', 'age', 'state', 'district', 'pin_code',
            'blood_group', 'photo', 'dob', 'gender', 'profession'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
                'autocomplete': 'email',
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number',
                'autocomplete': 'tel',
                'inputmode': 'tel',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full residential address',
            }),
            'aadhaar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12-digit Aadhaar number',
                'inputmode': 'numeric',
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's name (optional)",
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 18,
                'max': 65,
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'District',
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit pin code',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6}',
            }),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'dob': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'profession': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')
        dob = cleaned_data.get('dob')
        contact = cleaned_data.get('contact')
        aadhaar = cleaned_data.get('aadhaar')
        pin_code = cleaned_data.get('pin_code')
        
        # Validate age
        if age and (age < 18 or age > 65):
            raise ValidationError('Age must be between 18 and 65 years')
        
        # Validate DOB
        if dob and dob >= date.today():
            raise ValidationError('Date of birth cannot be in future')
        
        # Validate mobile
        if contact:
            if not re.match(r'^\d{10,15}$', contact.replace(' ', '').replace('-', '')):
                raise ValidationError('Invalid mobile number format')
        
        # Check duplicate aadhaar
        if aadhaar and Donor.objects.filter(aadhaar=aadhaar).exists():
            raise ValidationError('This Aadhaar number is already registered')
        
        return cleaned_data


class DonationRequestForm(forms.ModelForm):
    """Form for donation requests"""
    
    class Meta:
        model = DonationRequest
        fields = [
            'name', 'age', 'blood_group', 'weight',
            'hospital_report', 'last_donation_date',
            'requested_scheduleddate'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 18,
                'max': 65,
            }),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 45,
                'step': 0.5,
                'placeholder': 'Weight in kg (min 45kg)',
            }),
            'hospital_report': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'last_donation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'requested_scheduleddate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and weight < 45:
            raise ValidationError('Minimum weight requirement is 45 kg')
        return weight


# ============================================================================
# RECIPIENT FORMS
# ============================================================================

class RecipientRegistrationForm(forms.ModelForm):
    """Form for recipient registration"""
    
    class Meta:
        model = Recipient
        fields = [
            'name', 'email', 'contact', 'address', 'id_proof',
            'age', 'gender', 'state', 'district', 'pin_code'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number',
                'inputmode': 'tel',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address',
            }),
            'id_proof': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID Proof number',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'District',
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit pin code',
            }),
        }


class RecipientRequestForm(forms.ModelForm):
    """Form for recipient blood requests"""
    
    class Meta:
        model = RecipientRequest
        fields = [
            'patient_name', 'blood_group', 'units_required',
            'address', 'patient_report', 'photo', 'id_proof',
            'requisition_form'
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Patient's name",
            }),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50,
                'placeholder': 'Units required',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hospital/Medical center address',
            }),
            'patient_report': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'id_proof': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'requisition_form': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
        }


# ============================================================================
# HOSPITAL FORMS
# ============================================================================

class HospitalClinicRegistrationForm(forms.ModelForm):
    """Form for hospital/clinic registration"""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )
    
    class Meta:
        model = HospitalClinic
        fields = [
            'organization_name', 'related_blood_bank', 'state',
            'district', 'pin_code', 'login_id', 'contact', 'location'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital/Clinic name',
            }),
            'related_blood_bank': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Associated blood bank',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'District',
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit pin code',
            }),
            'login_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique login ID',
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number',
                'inputmode': 'tel',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full location/address',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match')
        
        if password and len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        return cleaned_data


class HospitalBloodRequestForm(forms.ModelForm):
    """Form for hospital blood requests"""
    
    class Meta:
        model = HospitalBloodRequest
        fields = [
            'organization_name', 'blood_group', 'units_required', 'purpose'
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital name',
            }),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 50,
                'placeholder': 'Units required',
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Purpose of blood requirement',
            }),
        }


# ============================================================================
# ADMIN FORMS
# ============================================================================

class AdminRegistrationForm(forms.ModelForm):
    """Form for admin registration"""
    name = forms.CharField(
        max_length=150,
        label='Full Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name',
        })
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })
    )
    
    class Meta:
        model = AdminProfile
        fields = ['mobile_number']
        widgets = {
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile number',
                'inputmode': 'tel',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match')
        
        if password and len(password) < 8:
            raise ValidationError('Password must be at least 8 characters')
        
        return cleaned_data


# ============================================================================
# BLOOD STOCK FORMS
# ============================================================================

class BloodStockForm(forms.ModelForm):
    """Form for managing blood stock"""
    
    class Meta:
        model = BloodStock
        fields = ['blood_group', 'units', 'date_collected']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'units': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Number of units',
            }),
            'date_collected': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
    
    def clean_units(self):
        units = self.cleaned_data.get('units')
        if units and units < 0:
            raise ValidationError('Units cannot be negative')
        return units
