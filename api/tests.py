from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient

from api.models import User
from api.serializers import UserRequestCodeSerializer, UserAuthSerializer
from api.service import generate_invite_code, generate_auth_code


class TestUserRequestCodeView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_user_create(self):
        data = {
            'phone':
                '79260000000'
        }
        response = self.client.post(
            path=reverse('api:request_code'),
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['message'],
            'verification code sent'
        )

    def test_generate_invite_code(self):
        invite_code = generate_invite_code()
        assert len(invite_code) == 6
        assert invite_code.isupper()
        assert invite_code.isalnum()

    def test_generate_auth_code(self):
        auth_code = generate_auth_code()
        assert len(auth_code) == 4
        assert auth_code.isnumeric()

    def tearDown(self):
        pass


class TestValidators(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(
            phone='79260000000',
            password='1111',
            password_created_on=timezone.now()
        )
        self.client.force_authenticate(user=self.user)

    def test_phone_number(self):

        with self.assertRaisesMessage(ValidationError,
                                      "phone number must start with '7'"
                                      ):
            serializer = UserRequestCodeSerializer(data={
                'phone':
                    '89260000000'
            }
            )
            serializer.is_valid(raise_exception=True)

    def test_phone_number_is_numeric(self):
        with self.assertRaisesMessage(ValidationError,
                                      "Phone number must contain only digits"
                                      ):
            serializer = UserRequestCodeSerializer(data={
                'phone':
                    '7f2f0000000'
            }
            )
            serializer.is_valid(raise_exception=True)

    def test_phone_number_is_mobile(self):
        with self.assertRaisesMessage(ValidationError,
                                      "only mobile phone numbers supported"
                                      ):
            serializer = UserRequestCodeSerializer(data={
                'phone':
                    '74990000000'
            }
            )
            serializer.is_valid(raise_exception=True)

    def test_auth_code_len(self):
        with self.assertRaisesMessage(ValidationError,
                                      "authorization code must contain 4 digits"
                                      ):
            serializer = UserAuthSerializer(data={
                'phone':
                    '79260000000',
                'password':
                    '11111'
            }
            )
            serializer.is_valid(raise_exception=True)

    def test_auth_code_isnumeric(self):
        with self.assertRaisesMessage(ValidationError,
                                      "authorization code must contain only digits"
                                      ):
            serializer = UserAuthSerializer(data={
                'phone':
                    '79260000000',
                'password':
                    'AAAA'
            }
            )
            serializer.is_valid(raise_exception=True)


class TestUserAuthView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(
            phone='79260000000',
            password='1111',
            password_created_on=timezone.now()
        )

    def tearDown(self):
        pass


class TestUserProfileView(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user_1 = User.objects.create(
            phone='79260000000',
            invite_code='O22QRB',
            activated_invite_code=None,
            date_joined=timezone.now(),
            password='1111',
            password_created_on=timezone.now()
        )
        self.user_2 = User.objects.create(
            phone='79260000001',
            invite_code='O22QRC',
            activated_invite_code=None,
            date_joined=timezone.now(),
            password='1112',
            password_created_on=timezone.now()
        )
        self.client.force_authenticate(self.user_1)
        self.client.force_authenticate(self.user_2)

    def test_list_profile(self):
        response = self.client.get(
            reverse('api:user_profile',
                    kwargs={
                        'pk': self.user_1.pk
                    }
                    )
        )

        self.assertEqual(
            response.data,
            {
                'phone': self.user_1.phone,
                'invite_code': self.user_1.invite_code,
                'activated_invite_code': None,
                'invited_users': None
            }
        )

    def test_invite_code_activation(self):
        kwargs = {'pk': self.user_2.pk}
        data = {
            'phone': self.user_2.phone,
            'activated_invite_code': self.user_1.invite_code
        }
        response = self.client.patch(
            path=reverse(
                'api:user_profile',
                kwargs=kwargs
            ),
            data=data
        )
        self.assertEqual(
            response.data,
            data
        )

    def tearDown(self):
        pass
