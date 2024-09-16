from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrIsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS 
                    or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user == obj.author 
                 or request.user.is_staff or request.user.is_admin)
        )
