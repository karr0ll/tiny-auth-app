from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserRequestCodeSerializer, UserAuthSerializer, UserRetrieveProfileSerializer, \
    UserActivateInviteCodeSerializer


class UserRequestCodeView(CreateAPIView):
    """
    View for user registration and auth code request or
    auth code request if user is registered
    """
    serializer_class = UserRequestCodeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
                {
                    'message': f"Verification code sent",
                    'user_id': instance.id
                }, status.HTTP_201_CREATED
            )


class UserAuthView(UpdateAPIView):
    serializer_class = UserAuthSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        queryset = User.objects.filter(pk=pk)
        return queryset

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', None)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        access_token = serializer.data.get('access_token', None)
        return Response(
            {
                'message': f"user authenticated",
                'access_token': access_token
            }, status.HTTP_200_OK
        )


class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserRetrieveProfileSerializer
        else:
            return UserActivateInviteCodeSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        queryset = User.objects.filter(pk=pk)
        return queryset
