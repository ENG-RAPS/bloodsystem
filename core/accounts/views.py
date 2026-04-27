from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import render

from .models import (
    User, Location, BloodInventory, Request,
    Donation, Notification, SystemLog, GlobalSettings
)

from .serializers import (
    UserSerializer, LocationSerializer,
    BloodInventorySerializer, RequestSerializer,
    DonationSerializer, NotificationSerializer,
    SystemLogSerializer, GlobalSettingsSerializer
)

from .permissions import IsSuperAdmin, IsAdminOrSuperAdmin


# =====================================================
# TEMPLATE VIEWS (HTML)
# =====================================================
def home(request):
    return render(request, "accounts/home.html")

def login_page(request):
    return render(request, "accounts/login.html")

def register_page(request):
    return render(request, "accounts/register.html")

def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')


# =====================================================
# AUTHENTICATION API ENDPOINTS
# =====================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """Login endpoint that returns token"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'success': True,
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'blood_type': user.blood_type,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """Logout endpoint that deletes token"""
    try:
        request.user.auth_token.delete()
        return Response({'success': True, 'message': 'Logged out successfully'})
    except:
        return Response({'success': True, 'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """Register endpoint"""
    data = request.data
    
    if User.objects.filter(username=data.get('username')).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=data.get('email')).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user info"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'blood_type': user.blood_type,
        'location': user.location_id,
        'is_active_donor': user.is_active_donor,
    }, status=status.HTTP_200_OK)


# =====================================================
# USERS
# =====================================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminOrSuperAdmin()]
        elif self.action == 'register':
            return [AllowAny()]
        elif self.action in ['destroy', 'update', 'partial_update']:
            return [IsAdminOrSuperAdmin()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Admins can see all users
        if user.role in ['admin', 'super_admin']:
            return User.objects.all()
        # Regular users can only see themselves
        return User.objects.filter(pk=user.pk)

    def perform_destroy(self, instance):
        """Only super admin can delete users"""
        if self.request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    def perform_create(self, serializer):
        role = serializer.validated_data.get('role', '').strip().lower()
        if role == 'super_admin' and self.request.user.role != 'super_admin':
            raise PermissionDenied('Only super admin can create another super admin')
        serializer.save()

    def perform_update(self, serializer):
        """Only admins can update users"""
        if self.request.user.role not in ['admin', 'super_admin']:
            return Response(
                {'error': 'Only admins can update users'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    @action(detail=False, methods=['POST'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def profile(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAdminOrSuperAdmin])
    def all_users(self, request):
        """Get all users - admin only"""
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def nearby_donors(self, request):
        if not request.user.location:
            return Response([], status=status.HTTP_200_OK)

        donors = User.objects.filter(
            location=request.user.location,
            is_active_donor=True,
            role__in=['donor', 'both']
        )
        return Response(self.get_serializer(donors, many=True).data)


# =====================================================
# LOCATION
# =====================================================
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['GET'])
    def by_city(self, request):
        city = request.query_params.get('city')

        if not city:
            return Response(
                {"error": "city parameter required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = Location.objects.filter(city__iexact=city)
        return Response(self.get_serializer(qs, many=True).data)


# =====================================================
# BLOOD INVENTORY
# =====================================================
class BloodInventoryViewSet(viewsets.ModelViewSet):
    queryset = BloodInventory.objects.all()
    serializer_class = BloodInventorySerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def perform_create(self, serializer):
        """Log inventory creation"""
        serializer.save()

    def perform_update(self, serializer):
        """Log inventory update"""
        serializer.save()

    def perform_destroy(self, instance):
        """Only super admin can delete inventory"""
        if self.request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can delete inventory'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['GET'])
    def by_location_and_type(self, request):
        qs = BloodInventory.objects.all()

        location_id = request.query_params.get('location_id')
        blood_type = request.query_params.get('blood_type')

        if location_id:
            qs = qs.filter(location_id=location_id)

        if blood_type:
            qs = qs.filter(blood_type=blood_type)

        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['POST'])
    def add_units(self, request, pk=None):
        obj = self.get_object()

        try:
            units = int(request.data.get('units', 0))
        except (TypeError, ValueError):
            return Response(
                {"error": "units must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if units < 0:
            return Response(
                {"error": "units cannot be negative"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj.units_available += units
        obj.save()

        return Response({"status": "updated", "total_units": obj.units_available})


# =====================================================
# BLOOD REQUEST
# =====================================================
class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ['admin', 'super_admin']:
            return Request.objects.all()

        return Request.objects.filter(requester=user)

    def get_permissions(self):
        if self.action in ['destroy', 'partial_update']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        req = serializer.save(requester=self.request.user)

    def perform_destroy(self, instance):
        """Only super admin can delete requests"""
        if self.request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can delete requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminOrSuperAdmin])
    def approve(self, request, pk=None):
        obj = self.get_object()

        obj.status = 'approved'
        obj.approved_by = request.user
        obj.approved_at = timezone.now()
        obj.save()

        return Response({"status": "approved"})

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminOrSuperAdmin])
    def reject(self, request, pk=None):
        obj = self.get_object()

        obj.status = 'rejected'
        obj.approved_by = request.user
        obj.save()

        return Response({"status": "rejected"})


# =====================================================
# DONATION
# =====================================================
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'super_admin']:
            return Donation.objects.all()
        return Donation.objects.filter(donor=user)

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)

    def perform_destroy(self, instance):
        """Only super admin can delete donations"""
        if self.request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can delete donations'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


# =====================================================
# NOTIFICATION
# =====================================================
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'super_admin']:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=user)

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update', 'create']:
            return [IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        """Only super admin can delete notifications"""
        if self.request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can delete notifications'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
