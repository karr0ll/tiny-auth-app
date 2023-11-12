from django.urls import path

from api.apps import UserConfig
from api.views import (UserRequestCodeView,
                         UserAuthView,
                         UserProfileView
                         )

app_name = UserConfig.name

urlpatterns = [
    path('request-auth-code/',
         UserRequestCodeView.as_view(), name='request_code'),
    path('auth/user/<int:pk>/',
         UserAuthView.as_view(), name='auth_user'),
    path('profile/user/<int:pk>/',
         UserProfileView.as_view(), name='user_profile'),
]
