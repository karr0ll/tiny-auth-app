from datetime import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from config.validators import PhoneNumberValidator
from users.models import User
from users.service.code_generators import (generate_invite_code,
                                           generate_auth_code)

from users.service.code_sender import send_auth_code


class UserRequestCodeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    phone = serializers.CharField(
        max_length=16,
        required=True
    )
    password = serializers.CharField(
        required=False,
        write_only=True
    )
    password_created_on = serializers.HiddenField(
        default=datetime.now(),
        write_only=True
    )

    def create(self, validated_data):
        phone = validated_data['phone']
        auth_code = generate_auth_code()
        queryset = User.objects.filter(phone=phone)
        if not queryset.exists():
            user = User.objects.create(
                phone=phone,
                date_joined=None,
                password_created_on=timezone.now(),
                is_active=False
            )
            send_auth_code(auth_code)
            user.set_password(auth_code)
            user.save()
            return user
        else:
            user = User.objects.get(phone=phone)
            send_auth_code(auth_code)
            user.set_password(auth_code)
            user.password_created_on = timezone.now()
            user.save()
            return user

    class Meta:
        model = User
        fields = (
            'phone',
            'password',
            'password_created_on',
            'id'
        )
        validators = [
            PhoneNumberValidator(field='phone'),
            # TokenLifeValidator(field='auth_code_created_at'),
            # PasswordValidator(field='password'),
        ]


class UserAuthSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=16,
        required=True
    )
    password = serializers.CharField(
        required=False,
        write_only=True
    )
    invite_code = serializers.CharField(
        max_length=6,
        required=False,
        write_only=True
    )
    access_token = serializers.SerializerMethodField(
        read_only=True
    )

    def update(self, instance, validated_data):
        phone = validated_data['phone']
        auth_code = validated_data['password']
        invite_code = generate_invite_code()
        user = User.objects.get(phone=phone)
        if user.check_password(auth_code):

            # Передача в метод создания токена объекта пользователя
            access_token = str(AccessToken.for_user(user))

            # Проверка введенного кода.
            # Если пользователь не проходил аутентификацию прежде -
            # генерируется invite code.
            if user.last_login is None:
                user.invite_code = invite_code
                user.date_joined = timezone.now()
                user.last_login = timezone.now()
                user.is_active = True
                # user_obj.password = None #TODO: нужно ли делать что-то с паролем после успешной аутентификации?
                user.save()
                validated_data.update(access_token=access_token)

            # Проверка введенного кода.
            # Если пользователь уже проходил аутентификацию -
            # в базу никакие изменения не вносятся.
            else:
                user.last_login = timezone.now()
                # user_obj.password = None #TODO: нужно ли делать что-то с паролем после успешной аутентификации?
                user.save()
                validated_data.update(access_token=access_token)
        else:
            raise serializers.ValidationError(
                'Authentication code is not valid'
            )
        return user

    def get_access_token(self, user: User) -> str:
        auth_code: str = self.validated_data.get('password', None)
        if auth_code is not None:
            if user.check_password(auth_code):
                return str(AccessToken.for_user(user))
        else:
            return None

    class Meta:
        model = User
        fields = (
            'phone',
            'password',
            'invite_code',
            'access_token'
        )
        validators = [
            PhoneNumberValidator(field='phone'),
            # TokenLifeValidator(field='auth_code_created_at'),
            # PasswordValidator(field='password'),
        ]


class UserRetrieveProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=16)
    invite_code = serializers.CharField(
        max_length=6,
        required=False,
        read_only=True
    )
    activated_invite_code = serializers.CharField(
        max_length=6,
        required=False
    )
    invited_users = serializers.SerializerMethodField(read_only=True)

    def get_invited_users(self, instance):
        invited_users_queryset = User.objects.filter(
            invite_code=instance.invite_code
        )
        invited_users = []
        for user in invited_users_queryset:
            if instance.pk != user.pk:
                invited_users.append(
                    {
                        'id': user.id,
                        'phone': user.phone
                    }
                )
        if len(invited_users) == 0:
            return None
        else:
            return invited_users

    class Meta:
        model = User
        fields = (
            'phone',
            'invite_code',
            'activated_invite_code',
            'invited_users'
        )


class UserActivateInviteCodeSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=16)
    activated_invite_code = serializers.CharField(
        max_length=6
    )

    def update(self, instance, validated_data):
        activate_invite_code = validated_data.get('activated_invite_code', None)
        if activate_invite_code is not None:
            if all(
                    [
                        (User.objects.filter(
                            invite_code=activate_invite_code
                        ).exists()
                        ),
                        (instance.activated_invite_code is None),
                        (activate_invite_code != instance.invite_code)
                    ]
            ):
                instance.activated_invite_code = activate_invite_code
                instance.save()
                return instance
            else:
                if not User.objects.filter(
                        invite_code=activate_invite_code
                ).exists():
                    raise serializers.ValidationError(
                        {
                            'error_message': "invite code not found"
                        }
                    )
                if instance.activated_invite_code is not None:
                    raise serializers.ValidationError(
                        {
                            'error_message': "user has activated invite code"
                        }
                    )
                if activate_invite_code == instance.invite_code:
                    raise serializers.ValidationError(
                        {
                            'error_message':
                                "user's own invite code can't be activated"
                        }
                    )
        else:
            raise serializers.ValidationError(
                {'activated_invite_code': 'this field is required'}
            )

    class Meta:
        model = User
        fields = (
            'phone',
            'activated_invite_code'
        )
