from datetime import datetime

import jwt
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from users.models import User
from users.service.code_generators import generate_invite_code, generate_auth_code

from users.service.code_sender import send_auth_code


class UserCreateSerializer(serializers.ModelSerializer, TokenObtainSerializer):
    phone = serializers.CharField(max_length=16)
    invite_code = serializers.CharField(
        max_length=6,
        required=False,
        write_only=True
    )
    password = serializers.CharField(
        max_length=4,
        required=False,
        write_only=True
    )
    password_created_at = serializers.HiddenField(default=datetime.now(), write_only=True)

    class Meta:
        model = User

        fields = (
            'phone',
            'invite_code',
            'is_authenticated',
            'password',
            'password_created_at'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    def create(self, validated_data):
        phone = validated_data['phone']

        invite_code = generate_invite_code()
        password = generate_auth_code()

        queryset = User.objects.filter(phone=phone)

        # Создание новой записи,
        # если пользователя с таким номером нет в базе
        if not queryset.exists():
            user = User.objects.create(
                phone=phone,
                password=password
            )
            send_auth_code(password)
            user.save()

        for item in queryset:
            try:
                password = validated_data['password']
                # Проверка введенного кода.
                # Если пользователь не проходил аутентификацию прежде -
                # генерируется invite code.
                if password == item.auth_code and not item.is_authenticated:

                    queryset.update(
                        phone=phone,
                        invite_code=invite_code,
                        is_authenticated=True
                    )
                # Проверка введенного кода.
                # Если пользователь уже проходил аутентификацию -
                # в базу никакие изменения не вносятся.
                elif password == item.password and item.is_authenticated:
                    queryset.update(
                        phone=phone
                    )
                else:
                    queryset.update(
                        is_authenticated=False
                    )
                    raise serializers.ValidationError('Authorization code is not valid')
            except KeyError:
                send_auth_code(password)
                User.objects.update(
                    password=password
                )
        print(validated_data)
        return validated_data

    def validate(self, attrs):
        print(attrs)
        attrs.update({'password': ''})
        return super(UserCreateSerializer, self).validate(attrs)

