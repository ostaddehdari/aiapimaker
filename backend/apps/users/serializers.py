"""Explicit request/response shapes for OpenAPI and server-side validation."""

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    password = serializers.CharField(max_length=1024, write_only=True, trim_whitespace=False)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, max_length=1024)
    new_password = serializers.CharField(write_only=True, max_length=1024)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=200)
    token = serializers.CharField(max_length=200)
    new_password = serializers.CharField(write_only=True, max_length=1024)


class SessionRevokeSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
