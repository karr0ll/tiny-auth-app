from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from users.serializers import UserCreateSerializer


class UserCreateView(CreateAPIView):
    """
    Контроллер регистрации или авторизации пользователя
    """
    serializer_class = UserCreateSerializer


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

