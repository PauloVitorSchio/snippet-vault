import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_credentials():
    return {
        "email": "newuser@example.com",
        "password": "strong-pass-9x!",
        "display_name": "New User",
    }


@pytest.mark.django_db
class TestRegistration:
    def test_register_returns_token(self, api_client, user_credentials):
        response = api_client.post("/auth/register/", user_credentials, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"
        assert Token.objects.filter(user__email="newuser@example.com").exists()

    def test_duplicate_email_same_case(self, api_client, user_credentials):
        api_client.post("/auth/register/", user_credentials, format="json")
        response = api_client.post("/auth/register/", user_credentials, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_email_different_case(self, api_client, user_credentials):
        api_client.post("/auth/register/", user_credentials, format="json")
        dup = {**user_credentials, "email": "NEWUSER@EXAMPLE.COM"}
        response = api_client.post("/auth/register/", dup, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_rejected(self, api_client, user_credentials):
        weak = {**user_credentials, "email": "weak@example.com", "password": "12345"}
        response = api_client.post("/auth/register/", weak, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data["error"]["details"]


@pytest.mark.django_db
class TestLogin:
    def test_wrong_password_and_missing_user_same_message(self, api_client, user_credentials):
        api_client.post("/auth/register/", user_credentials, format="json")
        wrong_pw = api_client.post(
            "/auth/login/",
            {"email": user_credentials["email"], "password": "wrong-password-!!!"},
            format="json",
        )
        missing = api_client.post(
            "/auth/login/",
            {"email": "nobody@example.com", "password": "any-password-9!"},
            format="json",
        )
        assert wrong_pw.status_code == status.HTTP_401_UNAUTHORIZED
        assert missing.status_code == status.HTTP_401_UNAUTHORIZED
        assert wrong_pw.data["error"]["message"] == "Invalid credentials."
        assert missing.data["error"]["message"] == wrong_pw.data["error"]["message"]

    def test_inactive_user_same_as_invalid_credentials(self, api_client, user_credentials):
        api_client.post("/auth/register/", user_credentials, format="json")
        user = User.objects.get(email="newuser@example.com")
        user.is_active = False
        user.save(update_fields=["is_active"])
        response = api_client.post(
            "/auth/login/",
            {"email": user_credentials["email"], "password": user_credentials["password"]},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["error"]["message"] == "Invalid credentials."

    def test_login_twice_same_token(self, api_client, user_credentials):
        api_client.post("/auth/register/", user_credentials, format="json")
        body = {"email": user_credentials["email"], "password": user_credentials["password"]}
        first = api_client.post("/auth/login/", body, format="json")
        second = api_client.post("/auth/login/", body, format="json")
        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_200_OK
        assert first.data["token"] == second.data["token"]


@pytest.mark.django_db
class TestLogout:
    def test_logout_deletes_token_and_reuse_returns_401(self, api_client, user_credentials):
        reg = api_client.post("/auth/register/", user_credentials, format="json")
        token = reg.data["token"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        out = api_client.post("/auth/logout/")
        assert out.status_code == status.HTTP_204_NO_CONTENT
        assert not Token.objects.filter(key=token).exists()
        probe = api_client.post("/auth/logout/")
        assert probe.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_authorization_returns_401(self, api_client):
        response = api_client.post("/auth/logout/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
