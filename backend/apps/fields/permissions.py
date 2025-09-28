from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Regular users can only view (read-only).
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated user
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed for admin users
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to the owner or admin
        return (
            request.user.is_authenticated and 
            (obj.user == request.user or request.user.role == 'admin')
        )