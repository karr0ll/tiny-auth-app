from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.permissions import IsUser
from users.serializers import UserCreateSerializer, UserProfileSerializer


class UserCreateView(CreateAPIView):
    """
    Контроллер регистрации или авторизации пользователя
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    # def create(self, request, *args, **kwargs):
    #     # serializer = self.get_serializer(data=request.data)
    #     context = self.get_serializer_context()
    #     print(context)
    #     if serializer.is_valid():
    #         phone = serializer.initial_data['phone']
    #         uid = int(User.objects.get(phone=phone).id)
    #         try:
    #             serializer.initial_data['password']
    #         except KeyError:
    #             return Response(
    #                 {
    #                     'message': f"Verification code sent",
    #                 }, status.HTTP_201_CREATED
    #             )
    #         else:
    #             return Response(
    #                 {
    #                     'message': f"Phone verified",
    #                     'user_id': f"{uid}"
    #                 }, status.HTTP_200_OK
    #             )


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsUser]

    def get_queryset(self):
        queryset = User.objects.filter(pk=self.request.user.pk)
        return queryset

