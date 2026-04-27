from rest_framework.permissions import BasePermission


# -----------------------------
# SUPER ADMIN
# -----------------------------
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'super_admin'
        )


# -----------------------------
# ADMIN
# -----------------------------
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


# -----------------------------
# ADMIN OR SUPER ADMIN
# -----------------------------
class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['admin', 'super_admin']
        )


# -----------------------------
# REQUEST OWNER ONLY
# -----------------------------
class IsRequestOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and obj.requester == request.user
        )


# -----------------------------
# DONATION OWNER ONLY
# -----------------------------
class IsDonationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and obj.donor == request.user
        )


# -----------------------------
# FLEXIBLE RBAC (SAFE VERSION)
# -----------------------------
class IsRoleBasedAccessControl(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        required_roles = getattr(view, 'required_roles', None)

        if not required_roles:
            return False

        return request.user.role in required_roles