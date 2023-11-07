from datetime import datetime, timedelta
from typing import OrderedDict

from django.utils import timezone
from rest_framework.exceptions import ValidationError


class PhoneNumberValidator:

    def __init__(self, field: str) -> None:
        self.field: str = field

    def __call__(self, request_data: OrderedDict[str, str]) -> None:
        phone: str = dict(request_data).get(self.field)

        if not phone[0] == '7':
            raise ValidationError(
                "Phone number must start with '7'"
            )

        for i in phone:
            if i.isalpha():
                raise ValidationError(
                    "Phone number must contain only digits"
                )

        int_code: int = int(phone[1:4])
        if not 900 <= int_code <= 999:
            raise ValidationError(
                "Only mobile phone numbers supported"
            )


class TokenLifeValidator:

    def __init__(self, field: str) -> None:
        self.field: str = field

    def __call__(self, request_data: OrderedDict[str, datetime]) -> None:
        auth_code_created_at: datetime = request_data.get(self.field)
        token_life_time = auth_code_created_at + timedelta(minutes=3)
        if token_life_time < timezone.now():
            raise ValidationError(
                "Token expired"
            )









