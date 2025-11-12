from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Allow only Django superusers."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsAdmin(permissions.BasePermission):
    """Allow users with role='admin' (not superuser) or superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == "admin")
        )


class IsSeller(permissions.BasePermission):
    """Allow users with role='seller' or superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == "seller")
        )


class IsCustomer(permissions.BasePermission):
    """Allow users with role='customer' or superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == "customer")
        )


class IsAdminOrSeller(permissions.BasePermission):
    """Allow Admin, Seller, or SuperAdmin."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.role in ["admin", "seller"]
            )
        )


class ReadOnlyOrAdmin(permissions.BasePermission):
    """Allow anyone to read, but only Admins or SuperAdmins to write."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == "admin")
        )


class ReadOnlyOrAdminOrSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, must be admin or seller
        return (
            request.user.is_authenticated and 
            (request.user.role in ['admin', 'seller'] or request.user.is_superuser)
        )
