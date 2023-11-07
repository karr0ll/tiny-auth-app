from datetime import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from config.validators import PhoneNumberValidator
from users.models import User
from users.service.code_generators import generate_invite_code, generate_auth_code

from users.service.code_sender import send_auth_code


class UserCreateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=16)
    invite_code = serializers.CharField(
        max_length=6,
        required=False,
        write_only=True
    )
    password = serializers.CharField(
        required=False,
        write_only=True
    )
    password_created_on = serializers.HiddenField(default=datetime.now(), write_only=True)

    class Meta:
        model = User

        fields = (
            'phone',
            'invite_code',
            'password',
            'password_created_on',
        )

        validators = [
            PhoneNumberValidator(field='phone'),
            # TokenLifeValidator(field='auth_code_created_at'),
            # PasswordValidator(field='password'),
        ]

    def create(self, validated_data):
        phone = validated_data['phone']

        invite_code = generate_invite_code()
        auth_code = generate_auth_code()

        # Создание новой записи,
        # если пользователя с таким номером нет в базе

        queryset = User.objects.filter(phone=phone)
        if not queryset.exists():
            print('срабатывает if not queryset.exists()')
            user = User.objects.create(
                phone=phone,
                date_joined=None,
                password_created_on=timezone.now(),
                is_active=False
            )
            send_auth_code(auth_code)
            user.set_password(auth_code)
            user.save()
        else:
            try:
                auth_code = validated_data['password']

                user_obj = User.objects.get(phone=phone)
                if user_obj.check_password(auth_code):

                    # Передача в метод создания токена объекта пользователя

                    access_token = AccessToken.for_user(user_obj)

                    # Проверка введенного кода.
                    # Если пользователь не проходил аутентификацию прежде -
                    # генерируется invite code.

                    if user_obj.last_login is None:
                        print('срабатывает user_obj.last_login is None')

                        user_obj.invite_code = invite_code
                        user_obj.date_joined = timezone.now()
                        user_obj.last_login = timezone.now()
                        user_obj.is_active = True
                        user_obj.save()
                        validated_data['access_token'] = access_token

                    # Проверка введенного кода.
                    # Если пользователь уже проходил аутентификацию -
                    # в базу никакие изменения не вносятся.

                    else:
                        user_obj.last_login = timezone.now()
                        user_obj.save()
                        validated_data['access_token'] = access_token
                else:
                    raise serializers.ValidationError('Authentication code is not valid')
            except KeyError:

                # Отправка кода аутентификации существующему пользователю
                user_obj = User.objects.get(phone=phone)
                send_auth_code(auth_code)
                user_obj.set_password(auth_code)
                user_obj.password_created_on = timezone.now()
                user_obj.save()

        return validated_data

