from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'account'):
            return obj.account == request.user
        if hasattr(obj, 'dashboard'):
            return obj.dashboard.account == request.user
        return False