from rest_framework import permissions

class IsSuperuserOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow superuser to perform any action
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        # Allow the owner of the blog to perform actions
        return obj.user == request.user
    
from rest_framework.permissions import IsAuthenticated

class CustomPermission(IsAuthenticated):
    def has_permission(self, request, view):
        # Allow unauthenticated (anonymous) users to access the GET method
        if request.method == 'GET':
            return True
        # Require token-based authentication for other methods
        return super().has_permission(request, view)
