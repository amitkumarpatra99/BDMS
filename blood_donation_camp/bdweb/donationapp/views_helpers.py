"""
View helper functions for query optimization and common operations
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from django.db.models import Q, QuerySet, Prefetch
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from .models import (
    Donor, Recipient, DonationRequest, RecipientRequest,
    HospitalClinic, HospitalBloodRequest, CampSchedule, BloodStock
)

logger = logging.getLogger(__name__)


# ============================================================================
# DONOR HELPERS
# ============================================================================

def get_donor_with_requests(mobile_number: str) -> Optional[Tuple[Donor, QuerySet]]:
    """
    Get donor and their donation requests with optimized queries
    
    Args:
        mobile_number: Donor's mobile number
    
    Returns:
        Tuple of (Donor, donation_requests) or (None, None) if not found
    """
    try:
        donor = Donor.objects.prefetch_related(
            Prefetch('donation_requests')
        ).get(contact=mobile_number)
        
        donation_requests = donor.donation_requests.all().select_related('donor')
        return donor, donation_requests
    
    except Donor.DoesNotExist:
        logger.warning(f"Donor not found with mobile: {mobile_number}")
        return None, None
    except Exception as e:
        logger.error(f"Error fetching donor: {str(e)}")
        return None, None


def search_donors(query: str, limit: int = 10) -> QuerySet:
    """
    Search donors by name, email, or aadhaar
    
    Args:
        query: Search query
        limit: Maximum results to return
    
    Returns:
        QuerySet of matching donors
    """
    return Donor.objects.filter(
        Q(name__icontains=query) |
        Q(email__icontains=query) |
        Q(aadhaar__icontains=query)
    ).values_list('id', 'name', 'blood_group', 'contact')[:limit]


def get_donors_by_blood_group(blood_group: str) -> QuerySet:
    """
    Get all donors with a specific blood group
    
    Args:
        blood_group: Blood group code (e.g., 'A+', 'O-')
    
    Returns:
        QuerySet of donors
    """
    return Donor.objects.filter(blood_group=blood_group).only(
        'id', 'name', 'contact', 'blood_group', 'age'
    )


def get_eligible_donors(blood_group: str) -> QuerySet:
    """
    Get eligible donors (age 18-65) for a specific blood group
    
    Args:
        blood_group: Blood group code
    
    Returns:
        QuerySet of eligible donors
    """
    return Donor.objects.filter(
        blood_group=blood_group,
        age__gte=18,
        age__lte=65
    ).only('id', 'name', 'contact', 'blood_group')


# ============================================================================
# BLOOD STOCK HELPERS
# ============================================================================

def get_available_blood_stock() -> QuerySet:
    """
    Get all non-expired blood stock
    
    Returns:
        QuerySet of valid blood stock
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now().date() - timedelta(days=42)
    return BloodStock.objects.filter(
        date_collected__gte=cutoff_date,
        units__gt=0
    ).values('blood_group', 'units', 'expiry_date')


def get_blood_stock_by_group(blood_group: str) -> Dict[str, Any]:
    """
    Get blood stock details for a specific blood group
    
    Args:
        blood_group: Blood group code
    
    Returns:
        Dictionary with blood group info and available units
    """
    stock = BloodStock.objects.filter(
        blood_group=blood_group,
        units__gt=0
    ).aggregate(
        total_units=models.Sum('units'),
        count=models.Count('id')
    )
    
    return {
        'blood_group': blood_group,
        'total_units': stock['total_units'] or 0,
        'batches': stock['count'] or 0,
        'is_available': (stock['total_units'] or 0) > 0
    }


# ============================================================================
# HOSPITAL HELPERS
# ============================================================================

def get_hospital_requests(hospital_id: int) -> QuerySet:
    """
    Get all blood requests for a hospital with optimized queries
    
    Args:
        hospital_id: Hospital/Clinic ID
    
    Returns:
        QuerySet of hospital blood requests
    """
    return HospitalBloodRequest.objects.filter(
        hospital_id=hospital_id
    ).select_related('hospital').order_by('-created_at')


def search_hospitals(query: str, limit: int = 10) -> QuerySet:
    """
    Search hospitals by name, location, or district
    
    Args:
        query: Search query
        limit: Maximum results to return
    
    Returns:
        QuerySet of matching hospitals
    """
    return HospitalClinic.objects.filter(
        Q(organization_name__icontains=query) |
        Q(location__icontains=query) |
        Q(district__icontains=query)
    ).values_list('id', 'organization_name', 'location', 'contact')[:limit]


# ============================================================================
# DONATION REQUEST HELPERS
# ============================================================================

def get_pending_donation_requests() -> QuerySet:
    """
    Get all pending donation requests
    
    Returns:
        QuerySet of pending requests
    """
    from .models import StatusChoices
    
    return DonationRequest.objects.filter(
        status=StatusChoices.PENDING
    ).select_related('donor').order_by('-created_at')


def get_donor_donation_history(donor_id: int, limit: int = 10) -> QuerySet:
    """
    Get donation history for a donor
    
    Args:
        donor_id: Donor ID
        limit: Maximum records
    
    Returns:
        QuerySet of donation requests
    """
    return DonationRequest.objects.filter(
        donor_id=donor_id
    ).order_by('-created_at')[:limit]


# ============================================================================
# RECIPIENT REQUEST HELPERS
# ============================================================================

def get_pending_recipient_requests() -> QuerySet:
    """
    Get all pending recipient blood requests
    
    Returns:
        QuerySet of pending recipient requests
    """
    from .models import StatusChoices
    
    return RecipientRequest.objects.filter(
        status=StatusChoices.PENDING
    ).select_related('recipient').order_by('-created_at')


def get_requests_by_blood_group(blood_group: str) -> QuerySet:
    """
    Get all pending requests for a blood group
    
    Args:
        blood_group: Blood group code
    
    Returns:
        QuerySet of matching requests
    """
    from .models import StatusChoices
    
    return RecipientRequest.objects.filter(
        blood_group=blood_group,
        status=StatusChoices.PENDING
    ).select_related('recipient').order_by('-created_at')


# ============================================================================
# CAMP SCHEDULE HELPERS
# ============================================================================

def get_upcoming_camps(days_ahead: int = 30) -> QuerySet:
    """
    Get upcoming camp schedules
    
    Args:
        days_ahead: Number of days to look ahead
    
    Returns:
        QuerySet of upcoming camps
    """
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    return CampSchedule.objects.filter(
        date__range=[today, future_date]
    ).order_by('date', 'time')


def get_camps_by_location(state: str, district: str) -> QuerySet:
    """
    Get camps by location
    
    Args:
        state: State name
        district: District name
    
    Returns:
        QuerySet of matching camps
    """
    return CampSchedule.objects.filter(
        state=state,
        district=district,
        date__gte=timezone.now().date()
    ).order_by('date')


# ============================================================================
# STATISTICS & AGGREGATION
# ============================================================================

def get_donation_statistics() -> Dict[str, Any]:
    """
    Get donation statistics
    
    Returns:
        Dictionary with donation stats
    """
    from django.db.models import Count
    from .models import StatusChoices
    
    stats = {
        'total_donors': Donor.objects.count(),
        'total_recipients': Recipient.objects.count(),
        'pending_donations': DonationRequest.objects.filter(
            status=StatusChoices.PENDING
        ).count(),
        'accepted_donations': DonationRequest.objects.filter(
            status=StatusChoices.ACCEPTED
        ).count(),
        'pending_requests': RecipientRequest.objects.filter(
            status=StatusChoices.PENDING
        ).count(),
    }
    
    return stats


def get_blood_group_statistics() -> Dict[str, int]:
    """
    Get blood availability by group
    
    Returns:
        Dictionary with blood group availability
    """
    blood_groups = BloodStock.objects.filter(
        units__gt=0
    ).values('blood_group').annotate(
        total=models.Sum('units')
    ).order_by('blood_group')
    
    return {item['blood_group']: item['total'] for item in blood_groups}


def get_hospital_statistics() -> Dict[str, Any]:
    """
    Get hospital statistics
    
    Returns:
        Dictionary with hospital stats
    """
    from django.db.models import Count
    
    stats = {
        'total_hospitals': HospitalClinic.objects.count(),
        'pending_requests': HospitalBloodRequest.objects.filter(
            status='Pending'
        ).count(),
        'approved_requests': HospitalBloodRequest.objects.filter(
            status='Approved'
        ).count(),
    }
    
    return stats


# ============================================================================
# PERMISSION & VALIDATION HELPERS
# ============================================================================

def check_donor_eligibility(donor: Donor) -> Tuple[bool, str]:
    """
    Check if donor is eligible to donate
    
    Args:
        donor: Donor object
    
    Returns:
        Tuple of (is_eligible, reason)
    """
    if not (18 <= donor.age <= 65):
        return False, "Age must be between 18 and 65 years"
    
    # Check last donation date (56 days gap)
    last_donation = DonationRequest.objects.filter(
        donor=donor,
        status='Accepted'
    ).order_by('-created_at').first()
    
    if last_donation and last_donation.last_donation_date:
        from datetime import timedelta
        from django.utils import timezone
        
        days_since = (timezone.now().date() - last_donation.last_donation_date).days
        if days_since < 56:
            return False, f"Must wait {56 - days_since} more days before donating again"
    
    return True, "Eligible to donate"


# ============================================================================
# ERROR HANDLING
# ============================================================================

def handle_query_error(error: Exception, operation: str) -> JsonResponse:
    """
    Handle database query errors with logging
    
    Args:
        error: Exception object
        operation: Description of operation that failed
    
    Returns:
        JsonResponse with error message
    """
    logger.error(f"Database error during {operation}: {str(error)}")
    return JsonResponse(
        {
            'success': False,
            'message': f'An error occurred during {operation}. Please try again.'
        },
        status=500
    )
