from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    message = 'Only user has access to data'

    def has_object_permission(self, request, view, obj):
        if request.user.phone == obj.phone:
            return True
        return False, self.message
