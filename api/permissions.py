from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    message = {
        'permission_error':
            'Only profile owner can get access'
    }

    def has_object_permission(self, request, view, obj):
        if request.user.phone == obj.user.phone:
            return True
        return False, self.message
