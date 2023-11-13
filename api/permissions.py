from rest_framework.permissions import BasePermission


class IsUser(BasePermission):
    message = {
        'permission_error':
            'Only profile owner can get access'
    }

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            if request.user.phone == obj.phone:
                return True
        else:
            return False, self.message

