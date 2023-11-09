from django.urls import path

from users.apps import UserConfig
from users.views import UserRequestCodeView, UserAuthView, UserProfileView#, UserActivateInviteCodeView

app_name = UserConfig.name

urlpatterns = [
    path('request-auth-code/', UserRequestCodeView.as_view(), name='request_code'),
    path('auth/user/<int:pk>/', UserAuthView.as_view(), name='auth_user'),
    path('profile/user/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    # path('profile/user/<int:pk>/activate-invite-code/', UserActivateInviteCodeView.as_view(), name='activate_invite_code')
]
