from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    username = None

    phone = models.CharField(
        max_length=11,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Телефон'
    )

    invite_code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Инвайт-код пользователя'
    )

    activated_invite_code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Активированный инвайт-код'
    )

    date_joined = models.DateTimeField(
        default=timezone.now(),
        blank=True,
        null=True,
    )

    password = models.CharField(
        blank=False,
        null=True,
        verbose_name='Код авторизации'
    )

    password_created_on = models.DateTimeField(
        default=timezone.now(),
        blank=True,
        null=True,
        verbose_name='Код авторизации создан'
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return (
            f'Телефон: {self.phone}, '
            f'Инвайт-код: {self.invite_code}, '
            f'Активированный инвайт-код:{self.activated_invite_code} '
        )

    class Meta:
        verbose_name = ('Пользователь')
        verbose_name_plural = ('Пользователи')
