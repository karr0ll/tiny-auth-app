from django.urls import path

from users.apps import UserConfig
from users.views import UserCreateView, UserProfileView

app_name = UserConfig.name

urlpatterns = [
    path('auth/', UserCreateView.as_view(), name='login'),
    path('profile/<int:pk>', UserProfileView.as_view(), name='profile')
]