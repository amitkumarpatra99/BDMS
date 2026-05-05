import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
def generate_otp():
    otp = str(random.randint(100000, 999999))
    print(f"📦 OTP Generated: {otp}")
    return otp

def send_otp_to_mobile_user(mobile):
    otp = generate_otp()
    OTP.objects.create(mobile_number=mobile, otp=otp)
    send_sms_otp(mobile, otp)  
    
    return otp


def send_admin_otp(email, otp):
    subject = "Your Admin Login OTP"
    message = f"Your OTP for Admin login is: {otp}"
    send_mail(subject, message, "no-reply@yourdomain.com", [email])

def send_otp_to_hospital_email(hospital):
    otp_code = generate_otp()

    OTP.objects.create(mobile_number=hospital.contact, otp=otp_code)

    send_mail(
        subject='Your Hospital Login OTP',
        message=f'Your OTP for login is: {otp_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[hospital.user.email],
        fail_silently=False,
    )
    send_sms_otp(hospital.contact, otp_code)
    return otp_code
import requests
from django.conf import settings

def send_sms_otp(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        'authorization': settings.FAST2SMS_API_KEY,  
        'sender_id': 'FSTSMS',
        'message': f'Your OTP is {otp}',
        'language': 'english',
        'route': 'q',
        'numbers': mobile,
    }
    headers = {
        'cache-control': 'no-cache'
    }

    response = requests.post(url, data=payload, headers=headers)
    print(response.text) 