from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from rest_framework import serializers

User = get_user_model()


def normalize_auth_email(value: str) -> str:
    return (value or "").strip().lower()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=1)

    class Meta:
        model = User
        fields = ("email", "password", "display_name")

    def validate_email(self, value: str) -> str:
        normalized = normalize_auth_email(value)
        if not normalized:
            raise serializers.ValidationError("This field may not be blank.")
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def validate_display_name(self, value: str) -> str:
        return (value or "").strip()

    def validate_password(self, value: str) -> str:
        stripped = (value or "").strip()
        if not stripped:
            raise serializers.ValidationError("This field may not be blank.")
        email_for_check = normalize_auth_email(self.initial_data.get("email", ""))
        validate_password(stripped, User(email=email_for_check))
        return stripped

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        try:
            return User.objects.create_user(password=password, **validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            ) from None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, allow_blank=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        normalized = normalize_auth_email(value)
        if not normalized:
            raise serializers.ValidationError("This field may not be blank.")
        return normalized

    def validate_password(self, value: str) -> str:
        stripped = (value or "").strip()
        if not stripped:
            raise serializers.ValidationError("This field may not be blank.")
        return stripped


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "display_name")
