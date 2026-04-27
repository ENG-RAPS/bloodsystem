from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    LocationViewSet,
    BloodInventoryViewSet,
    RequestViewSet,
    DonationViewSet,
    NotificationViewSet,
    dashboard,
    admin_dashboard,
    home,
    login_page,
    register_page,
    login_api,
    logout_api,
    register_api,
    current_user,
)

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('locations', LocationViewSet)
router.register('inventory', BloodInventoryViewSet)
router.register('requests', RequestViewSet)
router.register('donations', DonationViewSet)
router.register('notifications', NotificationViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # API Endpoints
    path('api/auth/login/', login_api, name='login_api'),
    path('api/auth/logout/', logout_api, name='logout_api'),
    path('api/auth/register/', register_api, name='register_api'),
    path('api/auth/user/', current_user, name='current_user'),
    path('api/', include(router.urls)),
]