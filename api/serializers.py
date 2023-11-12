import datetime
from typing import Union

from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from config.validators import (PhoneNumberValidator,
                               AuthCodeLifeValidator,
                               PasswordValidator
                               )
from api.models import User
from api.service.code_generators import (generate_invite_code,
                                           generate_auth_code)

from api.service.code_sender import send_auth_code


class UserRequestCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for registration of new user and sending auth code
    or sending auth code for existing user
    """
    phone = serializers.CharField(
        max_length=16,
        required=True
    )
    password: str = serializers.CharField(
        required=False,
        write_only=True
    )
    password_created_on: datetime.datetime = serializers.HiddenField(
        default=timezone.now(),
        write_only=True
    )
    id: int = serializers.IntegerField(read_only=True)

    def create(self, validated_data: dict) -> User:
        phone: str = validated_data['phone']
        auth_code: str = generate_auth_code()
        queryset: QuerySet[User] = User.objects.filter(phone=phone)
        if not queryset.exists():
            user: User = User.objects.create(
                phone=phone,
                date_joined=None,
                password_created_on=timezone.now(),
                is_active=False
            )
            send_auth_code(phone, auth_code)
            user.set_password(auth_code)
            user.save()
            return user
        else:
            user: User = User.objects.get(phone=phone)
            send_auth_code(phone, auth_code)
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
        ]


class UserAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for verification of auth code input
    and returning access token
    """
    phone: str = serializers.CharField(
        max_length=16,
        required=True
    )
    password: str = serializers.CharField(
        required=True,
        write_only=True
    )
    invite_code: str = serializers.CharField(
        max_length=6,
        required=False,
        write_only=True
    )
    access_token: str = serializers.SerializerMethodField(
        read_only=True
    )

    def update(self, instance: User, validated_data: dict) -> User:
        phone: str = validated_data['phone']
        auth_code: str = validated_data['password']
        invite_code: str = generate_invite_code()
        user: User = User.objects.get(phone=phone)
        if user.check_password(auth_code):

            # Проверка введенного кода.
            # Если пользователь не проходил аутентификацию прежде -
            # генерируется invite code.
            if user.last_login is None:
                user.invite_code = invite_code
                user.date_joined = timezone.now()
                user.last_login = timezone.now()
                user.is_active = True
                user.save()

            # Проверка введенного кода.
            # Если пользователь уже проходил аутентификацию -
            # в базу никакие изменения не вносятся.
            else:
                user.last_login = timezone.now()
                user.save()
        else:
            raise serializers.ValidationError(
                {'error_message':
                    'authentication code is not valid'
                 }
            )
        return user

    def get_access_token(self, instance: User) -> Union[str, None]:
        auth_code: str = self.validated_data.get('password', None)
        if auth_code is not None:
            if instance.check_password(auth_code):
                return str(AccessToken.for_user(instance))
        else:
            return None

    class Meta:
        model = User
        fields = (
            'phone',
            'password',
            'invite_code',
            'access_token',
        )
        validators = [
            PhoneNumberValidator(field='phone'),
            AuthCodeLifeValidator(field='phone'),
            PasswordValidator(field='password'),
        ]


class UserRetrieveProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user info
    """
    phone: str = serializers.CharField(max_length=16)
    invite_code: str = serializers.CharField(
        max_length=6,
        required=False,
        read_only=True
    )
    activated_invite_code: str = serializers.CharField(
        max_length=6,
        required=False
    )
    invited_users: list[dict] = serializers.SerializerMethodField(read_only=True)

    def get_invited_users(self, instance: User) -> Union[None, list]:
        invited_users_queryset: QuerySet[User] = User.objects.filter(
            activated_invite_code=instance.invite_code
        )
        invited_users = []
        for item in invited_users_queryset:
            invited_users.append(
                {
                    'id': item.id,
                    'phone': item.phone
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
        validators = [
            PhoneNumberValidator(field='phone')
        ]


class UserActivateInviteCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user info
    """
    phone: str = serializers.CharField(max_length=16)
    activated_invite_code: str = serializers.CharField(
        max_length=6
    )

    def update(self, instance: User, validated_data: dict):
        activate_invite_code: str = validated_data.get(
            'activated_invite_code', None
        )
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
                            'error_message':
                                'user has already activated invite code'
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
