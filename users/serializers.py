from datetime import datetime

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer

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
    auth_code = serializers.CharField(
        max_length=4,
        required=False,
        write_only=True
    )
    auth_code_created_at = serializers.HiddenField(default=datetime.now(), write_only=True)
    id = serializers.IntegerField

    class Meta:
        model = User

        fields = (
            'phone',
            'invite_code',
            'is_authenticated',
            'auth_code',
            'auth_code_created_at',
        )

        validators = [
            PhoneNumberValidator(field='phone'),

        ]

    def create(self, validated_data):
        phone = validated_data['phone']

        invite_code = generate_invite_code()
        auth_code = generate_auth_code()

        queryset = User.objects.filter(phone=phone)

        # Создание новой записи,
        # если пользователя с таким номером нет в базе
        if not queryset.exists():
            user = User.objects.create(
                phone=phone,
                auth_code=auth_code
            )
            send_auth_code(auth_code)
            user.save()
        for item in queryset:
            try:
                auth_code = validated_data['auth_code']
                # Проверка введенного кода.
                # Если пользователь не проходил аутентификацию прежде -
                # генерируется invite code.
                if auth_code == item.auth_code and not item.is_authenticated:
                    queryset.update(
                        phone=phone,
                        invite_code=invite_code,
                        is_authenticated=True
                    )
                    validated_data['id'] = item.pk

                # Проверка введенного кода.
                # Если пользователь уже проходил аутентификацию -
                # в базу никакие изменения не вносятся.
                elif auth_code == item.auth_code and item.is_authenticated:
                    queryset.update(
                        phone=phone
                    )
                else:
                    raise serializers.ValidationError('Authorization code is not valid')
            except KeyError:
                send_auth_code(auth_code)
                User.objects.update(
                    auth_code=auth_code
                )
        return validated_data
