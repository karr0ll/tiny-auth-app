from datetime import datetime, timedelta
from typing import OrderedDict

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.models import User


class PhoneNumberValidator:

    def __init__(self, field: str) -> None:
        self.field: str = field

    def __call__(self, request_data: OrderedDict[str, str]) -> None:
        phone: str = dict(request_data).get(self.field)

        if not phone[0] == '7':
            raise ValidationError(
                {'invalid_phone_number': "phone number must start with '7'"}
            )

        for i in phone:
            if i.isalpha():
                raise ValidationError(
                    {'invalid_phone_number': "Phone number must contain only digits"}
                )

        int_code: int = int(phone[1:4])
        if not 900 <= int_code <= 999:
            raise ValidationError(
                {'invalid_phone_number': "only mobile phone numbers supported"}
            )


class AuthCodeLifeValidator:

    def __init__(self, field: str) -> None:
        self.field: str = field

    def __call__(self, request_data: OrderedDict[(str, str)]) -> None:
        phone = request_data.get(self.field)
        password_created_on: datetime = User.objects.get(phone=phone).password_created_on
        auth_code_life_time = password_created_on + timedelta(minutes=3)
        if auth_code_life_time < timezone.now():
            raise ValidationError(
                {'error_message': 'authorization code expired'}
            )


class PasswordValidator:

    def __init__(self, field: str) -> None:
        self.field: str = field

    def __call__(self, request_data: OrderedDict[str, str]):
        auth_code = dict(request_data).get(self.field)
        if len(auth_code) != 4:
            raise ValidationError(
                'authorization code must contain 4 digits'
            )

        if not auth_code.isnumeric():
            raise ValidationError(
                'authorization code must contain only digits'
            )










