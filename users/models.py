from django.contrib.auth.models import AbstractUser
from django.db import models


class User(models.Model):
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

    is_authenticated = models.BooleanField(
        default=False
    )

    auth_code = models.CharField(
        max_length=4,
        blank=False,
        null=False,
        verbose_name='Код авторизации'
    )

    auth_code_created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        blank=True,
        verbose_name='Код авторизации создан'
    )

    def __str__(self):
        return (
            f'Телефон: {self.phone}, '
            f'Инвайт-код: {self.invite_code}, '
            f'Активированный инвайт-код:{self.activated_invite_code} '
        )

    class Meta:
        verbose_name = ('Пользователь')
        verbose_name_plural = ('Пользователи')