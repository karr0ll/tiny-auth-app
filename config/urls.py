from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
      title="tiny-auth-app API Docs",
      default_version='v1',
      description="API methods documentation",
      license=openapi.License(name="BSD License")
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path('',
         schema_view.with_ui(
             'redoc',
             cache_timeout=0
         ),
         name='schema-redoc'
         ),
    path('api/v1/', include('api.urls', namespace='api')),
]
