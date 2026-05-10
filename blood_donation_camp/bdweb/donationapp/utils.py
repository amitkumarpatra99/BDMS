"""
Utility functions for the Blood Donation Camp application
Includes OTP generation, SMS sending, and email utilities
"""

import random
import logging
from typing import Optional, Dict, Any
from datetime import timedelta

import requests
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse

from .models import OTP, AdminOTP

logger = logging.getLogger(__name__)


# ============================================================================
# OTP GENERATION & VALIDATION
# ============================================================================

def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP (One Time Password)
    
    Args:
        length: Length of OTP (default: 6 digits)
    
    Returns:
        Random OTP string
    """
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    logger.info(f"OTP generated (length: {length})")
    return otp


def verify_otp(mobile_number: str, otp_code: str, max_age_minutes: int = 5) -> bool:
    """
    Verify if OTP is valid for a mobile number
    
    Args:
        mobile_number: Mobile number to verify
        otp_code: OTP code to verify
        max_age_minutes: Maximum age of OTP in minutes
    
    Returns:
        True if OTP is valid, False otherwise
    """
    try:
        otp_obj = OTP.objects.filter(
            mobile_number=mobile_number,
            otp=otp_code
        ).latest('created_at')
        
        if not otp_obj.is_valid():
            logger.warning(f"OTP expired for mobile: {mobile_number}")
            return False
        
        otp_obj.delete()  # Delete after verification
        logger.info(f"OTP verified successfully for mobile: {mobile_number}")
        return True
    
    except OTP.DoesNotExist:
        logger.warning(f"OTP not found for mobile: {mobile_number}")
        return False
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return False


def verify_admin_otp(email: str, otp_code: str) -> bool:
    """
    Verify admin OTP
    
    Args:
        email: Admin email
        otp_code: OTP code to verify
    
    Returns:
        True if OTP is valid, False otherwise
    """
    try:
        otp_obj = AdminOTP.objects.filter(
            email=email,
            otp=otp_code
        ).latest('created_at')
        
        if not otp_obj.is_valid():
            logger.warning(f"Admin OTP expired for email: {email}")
            return False
        
        otp_obj.delete()
        logger.info(f"Admin OTP verified for email: {email}")
        return True
    
    except AdminOTP.DoesNotExist:
        logger.warning(f"Admin OTP not found for email: {email}")
        return False
    except Exception as e:
        logger.error(f"Error verifying admin OTP: {str(e)}")
        return False


# ============================================================================
# SMS SENDING
# ============================================================================

def send_sms_otp(mobile_number: str, otp: str) -> Dict[str, Any]:
    """
    Send OTP via SMS using Fast2SMS API
    
    Args:
        mobile_number: Recipient's mobile number
        otp: OTP code to send
    
    Returns:
        Response dictionary with success status
    """
    if not settings.FAST2SMS_API_KEY:
        logger.error("FAST2SMS_API_KEY not configured")
        return {'success': False, 'error': 'SMS service not configured'}
    
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            'authorization': settings.FAST2SMS_API_KEY,
            'sender_id': 'BDCAMP',
            'message': f'Your OTP for Blood Donation Camp is: {otp}. Valid for 5 minutes.',
            'language': 'english',
            'route': 'q',
            'numbers': mobile_number,
        }
        headers = {'cache-control': 'no-cache'}
        
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info(f"SMS OTP sent successfully to {mobile_number}")
        return {'success': True, 'message': 'OTP sent successfully'}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send SMS to {mobile_number}: {str(e)}")
        return {'success': False, 'error': 'Failed to send SMS'}
    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {str(e)}")
        return {'success': False, 'error': 'An error occurred'}


# ============================================================================
# EMAIL SENDING
# ============================================================================

def send_admin_otp_email(email: str, otp: str) -> bool:
    """
    Send OTP via email for admin authentication
    
    Args:
        email: Admin email address
        otp: OTP code to send
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = "Blood Donation Camp - Admin Login OTP"
        message = f"""
        Your OTP for Blood Donation Camp Admin Login is: {otp}
        
        This OTP will expire in 5 minutes.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        Blood Donation Camp Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Admin OTP email sent to {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send admin OTP email to {email}: {str(e)}")
        return False


def send_donor_registration_email(email: str, donor_name: str) -> bool:
    """
    Send registration confirmation email to donor
    
    Args:
        email: Donor's email
        donor_name: Donor's name
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = "Welcome to Blood Donation Camp"
        message = f"""
        Dear {donor_name},
        
        Thank you for registering with Blood Donation Camp!
        
        Your registration has been completed successfully.
        You can now login and manage your donation requests.
        
        Best regards,
        Blood Donation Camp Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Registration email sent to {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send registration email to {email}: {str(e)}")
        return False


def send_hospital_otp_email(email: str, hospital_name: str, otp: str) -> bool:
    """
    Send OTP via email to hospital
    
    Args:
        email: Hospital's email
        hospital_name: Hospital name
        otp: OTP code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = "Blood Donation Camp - Hospital Login OTP"
        message = f"""
        Dear {hospital_name},
        
        Your OTP for Blood Donation Camp Hospital Login is: {otp}
        
        This OTP will expire in 5 minutes.
        
        If you didn't request this OTP, please contact support immediately.
        
        Best regards,
        Blood Donation Camp Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Hospital OTP email sent to {email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send hospital OTP email to {email}: {str(e)}")
        return False


# ============================================================================
# USER AUTHENTICATION HELPERS
# ============================================================================

def send_otp_to_mobile_user(mobile_number: str) -> Optional[str]:
    """
    Generate and send OTP to mobile user (Donor/Recipient)
    
    Args:
        mobile_number: User's mobile number
    
    Returns:
        OTP code if successful, None otherwise
    """
    try:
        otp = generate_otp()
        OTP.objects.create(mobile_number=mobile_number, otp=otp)
        
        result = send_sms_otp(mobile_number, otp)
        if result['success']:
            return otp
        
        logger.warning(f"OTP generated but SMS failed for {mobile_number}")
        return None
    
    except Exception as e:
        logger.error(f"Error in send_otp_to_mobile_user: {str(e)}")
        return None


def send_admin_otp(email: str) -> Optional[str]:
    """
    Generate and send OTP to admin email
    
    Args:
        email: Admin email address
    
    Returns:
        OTP code if successful, None otherwise
    """
    try:
        otp = generate_otp()
        AdminOTP.objects.create(email=email, otp=otp)
        
        if send_admin_otp_email(email, otp):
            return otp
        
        logger.warning(f"OTP generated but email failed for {email}")
        return None
    
    except Exception as e:
        logger.error(f"Error in send_admin_otp: {str(e)}")
        return None


def send_otp_to_hospital_email(hospital) -> Optional[str]:
    """
    Generate and send OTP to hospital
    
    Args:
        hospital: HospitalClinic object
    
    Returns:
        OTP code if successful, None otherwise
    """
    try:
        otp = generate_otp()
        OTP.objects.create(mobile_number=hospital.contact, otp=otp)
        
        # Send via email
        email_sent = send_hospital_otp_email(
            hospital.user.email if hospital.user else hospital.contact,
            hospital.organization_name,
            otp
        )
        
        # Also try SMS
        send_sms_otp(hospital.contact, otp)
        
        if email_sent:
            return otp
        
        logger.warning(f"OTP created but email failed for hospital: {hospital.organization_name}")
        return None
    
    except Exception as e:
        logger.error(f"Error in send_otp_to_hospital_email: {str(e)}")
        return None


# ============================================================================
# RESPONSE HELPERS
# ============================================================================

def json_response(success: bool, message: str, data: Optional[Dict] = None, status_code: int = 200) -> JsonResponse:
    """
    Create a standardized JSON response
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Optional data to include in response
        status_code: HTTP status code
    
    Returns:
        JsonResponse object
    """
    response_data = {
        'success': success,
        'message': message,
    }
    
    if data:
        response_data['data'] = data
    
    return JsonResponse(response_data, status=status_code) 