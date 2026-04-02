import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(email="user@example.com", password="pass1234!")
        assert user.email == "user@example.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("pass1234!")
        assert user.has_usable_password() is not False  # password is set and usable

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(email="User@EXAMPLE.COM", password="pass1234!")
        assert user.email == "user@example.com"

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError, match="Email address is required"):
            User.objects.create_user(email="", password="pass1234!")

    def test_create_user_str(self):
        user = User.objects.create_user(email="str@example.com", password="pass1234!")
        assert str(user) == "str@example.com"

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password="admin1234!")
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_requires_is_staff(self):
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com", password="admin1234!", is_staff=False
            )

    def test_create_superuser_requires_is_superuser(self):
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com", password="admin1234!", is_superuser=False
            )
