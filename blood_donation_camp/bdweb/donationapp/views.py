from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .utils import generate_otp, send_admin_otp ,send_otp_to_hospital_email,send_otp_to_mobile_user
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import donorLoginForm,recipientLoginForm,BloodStockForm,HospitalOTPForm,HospitalLoginForm,HospitalClinicRegistrationForm,AdminRegistrationForm,OTPForm,RecipientRequestForm,DonationRequestForm,AdminOTPVerificationForm,AdminLoginForm,donorregistrationForm,RecipientRegistrationForm
from .models import OTP,AdminOTP,DonationRequest,BloodStock,HospitalClinic,HospitalBloodRequest,RecipientRequest,AdminProfile,Recipient, UserRole,Donor,CampSchedule
import random
import re
from datetime import date

# Create your views here.
def home(request):
    return render(request, 'donationapp/home.html')
def vission(request):
    return render(request, 'donationapp/vission.html')
def mission(request):
    return render(request, 'donationapp/mission.html')
def team(request):
    return render(request, 'donationapp/team.html')
def gallery(request):
    return render(request, 'donationapp/gallery.html')


def _normalize_mobile(mobile):
    return re.sub(r"\D", "", mobile or "")


def _get_recipient_by_mobile(mobile):
    normalized_mobile = _normalize_mobile(mobile)
    if not normalized_mobile:
        return None

    last_10_digits = normalized_mobile[-10:]
    for recipient in Recipient.objects.all():
        recipient_mobile = _normalize_mobile(recipient.contact)
        if recipient_mobile == normalized_mobile or recipient_mobile[-10:] == last_10_digits:
            return recipient
    return None


def _get_donor_by_mobile(mobile):
    normalized_mobile = _normalize_mobile(mobile)
    if not normalized_mobile:
        return None

    last_10_digits = normalized_mobile[-10:]
    for donor in Donor.objects.all():
        donor_mobile = _normalize_mobile(donor.contact)
        if donor_mobile == normalized_mobile or donor_mobile[-10:] == last_10_digits:
            return donor
    return None


def donorlogin(request):
    if request.method == 'POST':
        form = donorLoginForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            donor = _get_donor_by_mobile(mobile)
            if not donor:
                messages.error(request, 'Donor not found. Please register first or use your registered mobile number.')
                return render(request, 'donationapp/donorlogin.html', {'form': form})

            request.session['mobile'] = donor.contact
            request.session['role'] = 'donor'
            try:
                send_otp_to_mobile_user(donor.contact)
            except Exception:
                messages.warning(request, 'OTP service is temporarily unavailable. Please try again in a moment.')
                return render(request, 'donationapp/donorlogin.html', {'form': form})
            return redirect('otp')
    else:
        form = donorLoginForm()
    return render(request, 'donationapp/donorlogin.html', {'form': form})


def donorsignin(request):
    if request.method == 'POST':
        form = donorregistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('donorlogin')
        else:
            print("Form errors:", form.errors) 
    else:
        form = donorregistrationForm()
    return render(request, 'donationapp/donorsignin.html', {'form': form})

def donationrequest(request):
    if request.session.get('role') != 'donor' or not request.session.get('mobile'):
        return redirect('donorlogin')  

    donor = _get_donor_by_mobile(request.session['mobile'])
    if not donor:
        return redirect('donorlogin')  

    if request.method == 'POST':
        form = DonationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = donor
            donation.save()
            return redirect('donordashboard')
    else:
        form = DonationRequestForm()

    return render(request, 'donationapp/donorrequest.html', {'form': form})

def recipientlogin(request):
    if request.method == 'POST':
        form = recipientLoginForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['mobile']
            recipient = _get_recipient_by_mobile(mobile)
            if not recipient:
                messages.error(request, 'Recipient not found. Please register first or use your registered mobile number.')
                return render(request, 'donationapp/recipientlogin.html', {'form': form})

            request.session['mobile'] = recipient.contact
            request.session['role'] = 'recipient'
            try:
                send_otp_to_mobile_user(recipient.contact)
            except Exception:
                # Keep login flow usable even if SMS provider is temporarily unavailable.
                messages.warning(request, 'OTP service is temporarily unavailable. Please try again in a moment.')
                return render(request, 'donationapp/recipientlogin.html', {'form': form})
            return redirect('otp')
    else:
        form = recipientLoginForm()
    return render(request, 'donationapp/recipientlogin.html', {'form': form})
def recipientsignin(request):
    if request.method == 'POST':
        form = RecipientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Recipient registered successfully!")
            return redirect('recipientlogin')  
    else:
        form = RecipientRegistrationForm()
    
    return render(request, 'donationapp/recipientsignin.html', {'form': form})
def recipientrequest(request):
    if request.session.get('role') != 'recipient' or not request.session.get('mobile'):
        return redirect('recipientlogin')  

    recipient = _get_recipient_by_mobile(request.session['mobile'])
    if not recipient:
        return redirect('recipientlogin')

    if request.method == 'POST':
        form = RecipientRequestForm(request.POST, request.FILES)
        if form.is_valid():
            recipient_request = form.save(commit=False)
            recipient_request.recipient = recipient
            recipient_request.save()
            return redirect('recipientdashboard')
    else:
        form = RecipientRequestForm()

    return render(request, 'donationapp/recipientrequest.html', {'form': form})

def hospital_login(request):
    form = HospitalLoginForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        login_id = form.cleaned_data['login_id']
        password = form.cleaned_data['password']

        try:
            if '@' in login_id:
                hospital = HospitalClinic.objects.get(login_id =login_id, password=password)
            else:
                hospital = HospitalClinic.objects.get(login_id=login_id, password=password)

            # Send OTP to email
            send_otp_to_hospital_email(hospital)
            request.session['hospital_id'] = hospital.id
            return redirect('hospital_otp')

        except HospitalClinic.DoesNotExist:
            form.add_error(None, 'Invalid login credentials.')

    return render(request, 'donationapp/hospitallogin.html', {'form': form})

from .forms import HospitalBloodRequestForm

def hospital_request_blood(request):
    if request.session.get('role') != 'clinic' or not request.session.get('mobile'):
        return redirect('hospital_login')

    hospital = HospitalClinic.objects.filter(contact=request.session['mobile']).first()
    if not hospital:
        return redirect('hospital_login')

    if request.method == 'POST':
        form = HospitalBloodRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.hospital = hospital
            form.cleaned_data['organization_name'] = hospital.organization_name  # Ensures consistency
            request_obj.organization_name = hospital.organization_name
            request_obj.save()
            messages.success(request, "Blood request submitted successfully!")
            return redirect('hospitaldashboard')
    else:
        form = HospitalBloodRequestForm(initial={'organization_name': hospital.organization_name})

    return render(request, 'donationapp/hospitalbloodrequest.html', {'form': form})


def hospital_otp(request):
    hospital_id = request.session.get('hospital_id')
    hospital = HospitalClinic.objects.filter(id=hospital_id).first()

    if request.method == 'POST':
        form = HospitalOTPForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp']
            latest_otp = OTP.objects.filter(mobile_number=hospital.contact).order_by('-created_at').first()
            if latest_otp and latest_otp.otp == otp_entered and latest_otp.is_valid():
                request.session['role'] = 'clinic'
                request.session['mobile'] = hospital.contact
                return redirect('hospitaldashboard')
            else:
                form.add_error('otp', 'Invalid or expired OTP')
    else:
        form = HospitalOTPForm()

    return render(request, 'donationapp/hospitalotp.html', {'form': form})


from django.contrib.auth.models import User

def hospital_register(request):
    if request.method == 'POST':
        form = HospitalClinicRegistrationForm(request.POST)
        if form.is_valid():
           
            login_id = form.cleaned_data['login_id']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=login_id,
                password=password
            )

            hospital = form.save(commit=False)
            hospital.user = user
            hospital.save()

            return redirect('hospital_login')
    else:
        form = HospitalClinicRegistrationForm()
    return render(request, 'donationapp/hospitalsignin.html', {'form': form})

def adminlogin(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate using email as username (if using email as username)
            user = authenticate(request, username=email, password=password)

            if user is not None and (user.is_superuser or UserRole.objects.filter(user=user, role='admin').exists()):
                request.session['email'] = email
                request.session['role'] = 'admin'

                # Generate and save OTP
                otp = generate_otp()
                AdminOTP.objects.create(email=email, otp=otp)
                send_admin_otp(email, otp)

                print(" Form is valid. OTP will be generated now.")
                print(" OTP saved to AdminOTP model.")
                print(f"Admin OTP: {otp}")

                return redirect('admin_otp_verify') 
            else:
                messages.error(request, "Invalid admin credentials.")

    else:
        form = AdminLoginForm()

    return render(request, 'donationapp/adminlogin.html', {'form': form})
def adminregister(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'donationapp/admin.html', {'error': 'Passwords do not match'})

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=password,
            is_staff=True
        )

        AdminProfile.objects.create(user=user, mobile_number=contact, otp='000000')
        UserRole.objects.create(user=user, role='admin')

        return redirect('dashboard')
    else:
        form = AdminRegistrationForm()

    return render(request, 'donationapp/admin.html', {'form': form})



def admin_list(request):
    admins = AdminProfile.objects.all()
    return render(request, 'donationapp/adminlist.html', {'admins': admins})

# Edit Admin View
def admin_edit(request, admin_id):
    admin = get_object_or_404(AdminProfile, id=admin_id)
    
    if request.method == 'POST':
        admin.user.first_name = request.POST['name']
        admin.user.email = request.POST['email']
        admin.mobile_number = request.POST['contact']
        admin.user.save()
        admin.save()
        return redirect('adminlist')
    
    return render(request, 'donationapp/adminedit.html', {'admin': admin})

# Delete Admin View
def admin_delete(request, admin_id):
    admin = get_object_or_404(AdminProfile, id=admin_id)
    
    if request.method == 'POST':
        admin.user.delete()
        return redirect('adminlist')
    
    return render(request, 'donationapp/admindelete.html', {'admin': admin})


def admin_reset_password(request, admin_id):
    admin = get_object_or_404(AdminProfile, id=admin_id)
    
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        if new_password == confirm_password:
            admin.user.set_password(new_password)
            admin.user.save()
            return redirect('adminlist')
        else:
            return render(request, 'admin/admin_reset_password.html', {'error': 'Passwords do not match'})
    
    return render(request, 'donationapp/resetpassword.html', {'admin': admin})


def otp(request):
    mobile = request.session.get('mobile')
    role = request.session.get('role')

    if not mobile or not role:
        return redirect('home')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            try:
                otp_obj = OTP.objects.filter(mobile_number=mobile).latest('created_at')
                if otp_obj.otp == otp_input and otp_obj.is_valid():
                    if role == 'donor':
                        if not _get_donor_by_mobile(mobile):
                            messages.error(request, "Donor account not found. Please login again.")
                            return redirect('donorlogin')
                        return redirect('donordashboard')
                    elif role == 'recipient':
                        if not _get_recipient_by_mobile(mobile):
                            messages.error(request, "Recipient account not found. Please login again.")
                            return redirect('recipientlogin')
                        return redirect('recipientdashboard')
                   
                else:
                    messages.error(request, "Invalid or expired OTP.")
            except OTP.DoesNotExist:
                messages.error(request, "OTP not found.")
    else:
        form = OTPForm()

    return render(request, 'donationapp/otp.html', {'form': form})


def admin_otp_verify(request):
    email = request.session.get('email')

    if not email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('adminlogin')

    if request.method == 'POST':
        form = AdminOTPVerificationForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            otp_entry = AdminOTP.objects.filter(email=email).order_by('-created_at').first()

            if otp_entry and otp_entry.otp == otp_input and otp_entry.is_valid():
                messages.success(request, "OTP Verified Successfully.")
                return redirect('dashboard')  # Change to your dashboard url
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = AdminOTPVerificationForm()

    return render(request, 'donationapp/adminotp.html', {'form': form})
def donordashboard(request):
    requests = DonationRequest.objects.filter()
    camps = CampSchedule.objects.all().order_by('-date')
    return render(request, 'donationapp/donordashboard.html', {'requests': requests , 'camps': camps})
def dashboard(request):
    donor_requests = DonationRequest.objects.all()
    recipient_requests = RecipientRequest.objects.all()
    hospital_requests = HospitalBloodRequest.objects.all()
   
    requests = DonationRequest.objects.filter()
    for r in requests:
        if r.status == 'Accepted' and not request.session.get(f'shown_{r.id}'):
            messages.success(request, 'You are eligible for donation.')
            request.session[f'shown_{r.id}'] = True

    return render(request, 'donationapp/dashboard.html', {
        'donor_requests': donor_requests,
        'recipient_requests': recipient_requests,
        'hospital_requests': hospital_requests,
        'requests': requests
    })

def update_donor_request(request, pk, action):
    req = get_object_or_404(DonationRequest, pk=pk)
    if action == 'accepted':
        req.status = 'Accepted'
        req.rejection_message = None
        req.save()
        return redirect('dashboard')
    elif action == 'rejected':
        return redirect('donor_rejection_message', pk=req.id)
    
def donor_rejection_message(request, pk):
    req = get_object_or_404(DonationRequest, pk=pk)
    if request.method == 'POST':
        msg = request.POST.get('message')
        req.status = 'Rejected'
        req.rejection_message = msg
        req.save()
        return redirect('dashboard')
    return render(request, 'donationapp/donor_rejection_message.html', {'req': req})
    

def update_recipient_request(request, pk, action):
    request_obj = get_object_or_404(RecipientRequest, pk=pk)
    request_obj.status = action.capitalize()
    request_obj.save()
    return redirect('dashboard')

def update_hospital_request(request, pk, action):
    request_obj = get_object_or_404(HospitalBloodRequest, pk=pk)
    request_obj.status = action.capitalize()
    request_obj.save()
    return redirect('dashboard')
def recipientdashboard(request):
    if request.session.get('role') != 'recipient' or not request.session.get('mobile'):
        return redirect('recipientlogin')

    recipient = _get_recipient_by_mobile(request.session['mobile'])
    if not recipient:
        return redirect('recipientlogin')

    stocks = BloodStock.objects.all().order_by('-date_collected')
    requests = RecipientRequest.objects.filter(recipient=recipient).order_by('-id')

    return render(request, 'donationapp/recipientdashboard.html', {
        'stocks': stocks,
        'recipient_requests': requests
    })
def hospitaldashboard(request):
 
    if request.session.get('role') != 'clinic' or not request.session.get('mobile'):
        return redirect('hospital_login')

   
    hospital = HospitalClinic.objects.filter(contact=request.session['mobile']).first()
    if not hospital:
        return redirect('hospital_login')

    
    hospital_requests = HospitalBloodRequest.objects.filter(hospital=hospital).order_by('-id')

    
    stocks = BloodStock.objects.all().order_by('-date_collected')

    return render(request, 'donationapp/hospitaldashboard.html', {
        'stocks': stocks,
        'hospital_requests': hospital_requests,
    })
def add_stock(request):
    if request.method == "POST":
        form = BloodStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_stock')
    else:
        form = BloodStockForm()
    return render(request, 'donationapp/addstock.html', {'form': form})

def manage_stock(request):
    stocks = BloodStock.objects.all()
    return render(request, 'donationapp/managestock.html', {'stocks': stocks})

def delete_expired_stock(request, pk):
    stock = BloodStock.objects.get(id=pk)
    if stock.is_expired():
        stock.delete()
    return redirect('manage_stock')

def manage_donors(request):
    if 'delete' in request.GET:
        donor_id = request.GET.get('delete')
        Donor.objects.filter(id=donor_id).delete()
        return redirect('manage_donors')

    donors = Donor.objects.all()
    return render(request, 'donationapp/managedonor.html', {'donors': donors})

def manage_recipients(request):
    if 'delete' in request.GET:
        recipient_id = request.GET.get('delete')
        Recipient.objects.filter(id=recipient_id).delete()
        return redirect('manage_recipients')

    recipients = Recipient.objects.all()
    return render(request, 'donationapp/managerecipient.html', {'recipients': recipients})

def manage_hospitals(request):
    if 'delete' in request.GET:
        hospital_id = request.GET.get('delete')
        HospitalClinic.objects.filter(id=hospital_id).delete()
        return redirect('manage_hospitals')

    hospitals = HospitalClinic.objects.all()
    return render(request, 'donationapp/managehospital.html', {'hospitals': hospitals})
def blood_stock_page(request):
    stocks = BloodStock.objects.all().order_by('-date_collected')
    return render(request, 'donationapp/bloodstock.html', {'stocks': stocks})

def manage_camps(request):
    camps = CampSchedule.objects.all().order_by('-date')
    return render(request, 'donationapp/manage_camps.html', {'camps': camps})

def add_camp(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        time = request.POST.get('time')
        state = request.POST.get('state')
        district = request.POST.get('district')
        address = request.POST.get('address')
        description = request.POST.get('description')

        CampSchedule.objects.create(
            title=title, date=date, time=time, state=state,
            district=district, address=address, description=description
        )
        return redirect('manage_camps')

    return render(request, 'donationapp/add_camp.html')
def camp_schedule_page(request):
    camps = CampSchedule.objects.all().order_by('-date')
    return render(request, 'donationapp/campschedule.html', {'camps': camps})