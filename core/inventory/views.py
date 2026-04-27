from datetime import timedelta

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponseForbidden
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import BloodInventory, Request, Donation, User


@login_required(login_url='/login/')
def report_page(request):
    if request.user.role not in ['admin', 'super_admin']:
        return HttpResponseForbidden('Admin access required to view reports.')

    return render(request, 'inventory/report.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_data(request):
    if request.user.role not in ['admin', 'super_admin']:
        return Response({'detail': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    threshold = 30
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    units_by_type = {
        item['blood_type']: item['total_units'] for item in
        BloodInventory.objects.values('blood_type').annotate(total_units=Sum('units_available'))
    }

    total_units = BloodInventory.objects.aggregate(total=Sum('units_available'))['total'] or 0
    low_stock_items = BloodInventory.objects.filter(units_available__lt=threshold).select_related('location')[:5]
    low_stock_locations = [
        {
            'location': item.location.name if item.location else 'Unknown',
            'blood_type': item.blood_type,
            'units': item.units_available,
        }
        for item in low_stock_items
    ]

    total_requests = Request.objects.count()
    pending_requests = Request.objects.filter(status='pending').count()
    approved_requests = Request.objects.filter(status='approved').count()
    rejected_requests = Request.objects.filter(status='rejected').count()
    completed_requests = Request.objects.filter(status='completed').count()

    total_donations = Donation.objects.count()
    donations_last_month = Donation.objects.filter(status='completed', completed_date__gte=month_ago).count()
    scheduled_donations = Donation.objects.filter(status='scheduled').count()

    active_donors = User.objects.filter(is_active_donor=True, role__in=['donor', 'both']).count()

    return Response({
        'total_units': total_units,
        'total_locations': BloodInventory.objects.values('location').distinct().count(),
        'low_stock_threshold': threshold,
        'low_stock_count': low_stock_items.count(),
        'units_by_type': units_by_type,
        'low_stock_locations': low_stock_locations,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'completed_requests': completed_requests,
        'total_donations': total_donations,
        'donations_last_month': donations_last_month,
        'scheduled_donations': scheduled_donations,
        'active_donors': active_donors,
    })
