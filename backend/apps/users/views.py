"""First-party session authentication; no external AI account/session is accessed."""

from datetime import timedelta
from urllib.parse import urlencode
from uuid import UUID

from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .security import check_login_allowed, login_identifiers, note_failed_login, note_successful_login
from .security_models import AuthDeviceSession, AuthEvent, session_digest
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SessionRevokeSerializer,
)


def csrf_failure(request, reason=""):
    return JsonResponse(
        {"error": {"code": "csrf_failed", "message": "Valid CSRF token required"}},
        status=403,
    )


def public_user(user):
    role = "admin" if user.is_superuser or (user.platform_role == "admin" and user.is_staff) else "user"
    return {
        "id": str(user.pk),
        "username": user.get_username(),
        "email": user.email,
        "role": role,
        "is_staff": user.is_staff,
    }


class PublicAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


@method_decorator(csrf_protect, name="dispatch")
class CsrfBootstrap(PublicAPIView):
    @extend_schema(
        responses={200: OpenApiResponse(description="A CSRF token for X-CSRFToken requests")}
    )
    def get(self, request):
        from django.middleware.csrf import get_token

        token = get_token(request)
        response = Response({"csrf_token": token})
        response["Cache-Control"] = "no-store"
        return response


@method_decorator(csrf_protect, name="dispatch")
class LoginView(PublicAPIView):
    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiResponse(description="Session cookie established"),
                   401: OpenApiResponse(description="Invalid credentials"),
                   429: OpenApiResponse(description="Temporarily locked")},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        keys = login_identifiers(request, username)
        if not check_login_allowed(keys):
            return Response(
                {"error": {"code": "login_locked", "message": "Try again later"}},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            note_failed_login(keys)
            AuthEvent.record("login_failed", request, user=None, identifier=keys[1][0], success=False)
            return Response(
                {"error": {"code": "invalid_credentials", "message": "Invalid username or password"}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        now = timezone.now()
        device = AuthDeviceSession.objects.create(
            user=user,
            session_hash=session_digest(request.session.session_key),
            label=str(request.headers.get("User-Agent", "Browser"))[:90],
            expires_at=now + timedelta(seconds=settings.SESSION_COOKIE_AGE),
        )
        request.session["auth_device_id"] = str(device.id)
        note_successful_login(keys)
        AuthEvent.record("login_success", request, user=user, identifier=keys[1][0], success=True)
        from django.middleware.csrf import get_token

        response = Response({
            "user": public_user(user),
            "session_id": str(device.id),
            "csrf_token": get_token(request),
        })
        response["Cache-Control"] = "no-store"
        return response


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description="Session revoked")})
    def post(self, request):
        key = request.session.session_key
        if key:
            AuthDeviceSession.objects.filter(
                user=request.user, session_hash=session_digest(key)
            ).update(revoked_at=timezone.now())
        AuthEvent.record("logout", request, user=request.user, success=True)
        logout(request)
        return Response({"status": "logged_out"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description="Current account and role")})
    def get(self, request):
        response = Response({"user": public_user(request.user)})
        response["Cache-Control"] = "no-store"
        return response


class DeviceSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse(description="Own active device sessions")})
    def get(self, request):
        active = AuthDeviceSession.objects.filter(
            user=request.user, revoked_at__isnull=True, expires_at__gt=timezone.now()
        ).order_by("-created_at")[:100]
        current_hash = session_digest(request.session.session_key)
        return Response(
            {"sessions": [
                {
                    "id": str(item.pk),
                    "label": item.label,
                    "created_at": item.created_at.isoformat(),
                    "expires_at": item.expires_at.isoformat(),
                    "current": item.session_hash == current_hash,
                }
                for item in active
            ]}
        )


@method_decorator(csrf_protect, name="dispatch")
class RevokeDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SessionRevokeSerializer,
        responses={200: OpenApiResponse(description="Own session revoked")},
    )
    def post(self, request):
        serializer = SessionRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["session_id"]
        item = AuthDeviceSession.objects.filter(pk=identifier, user=request.user).first()
        if not item:
            return Response({"error": {"code": "not_found"}}, status=404)
        item.revoked_at = timezone.now()
        item.save(update_fields=["revoked_at"])
        AuthEvent.record("session_revoked", request, user=request.user, success=True)
        if item.session_hash == session_digest(request.session.session_key):
            logout(request)
        return Response({"status": "revoked"})


@method_decorator(csrf_protect, name="dispatch")
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Password changed and other devices revoked")},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"error": {"code": "invalid_credentials", "message": "Current password incorrect"}},
                status=400,
            )
        new_password = serializer.validated_data["new_password"]
        try:
            validate_password(new_password, user)
        except DjangoValidationError as exc:
            return Response({"error": {"code": "weak_password", "details": exc.messages}}, status=400)
        old_key = request.session.session_key
        user.set_password(new_password)
        user.save(update_fields=["password"])
        update_session_auth_hash(request, user)
        current_hash = session_digest(request.session.session_key)
        now = timezone.now()
        # Invalidate other tracked devices while keeping this device alive after key rotation.
        device = AuthDeviceSession.objects.filter(
            user=user, session_hash=session_digest(old_key)
        ).first()
        AuthDeviceSession.objects.filter(user=user, revoked_at__isnull=True).exclude(
            pk=device.pk if device else None
        ).update(revoked_at=now)
        if device:
            device.session_hash = current_hash
            device.expires_at = now + timedelta(seconds=settings.SESSION_COOKIE_AGE)
            device.save(update_fields=["session_hash", "expires_at"])
        AuthEvent.record("password_changed", request, user=user, success=True)
        return Response({"status": "password_changed", "other_devices_revoked": True})


@method_decorator(csrf_protect, name="dispatch")
class PasswordResetRequestView(PublicAPIView):
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={202: OpenApiResponse(description="Non-enumerating request accepted")},
    )
    def post(self, request):
        if not settings.PASSWORD_RESET_ENABLED:
            return Response({"error": {"code": "reset_not_configured"}}, status=503)
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        users = get_user_model().objects.filter(email__iexact=email, is_active=True)
        for user in users:
            if not user.has_usable_password():
                continue
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            query = urlencode({"uid": uid, "token": token})
            url = settings.APP_PUBLIC_ORIGIN.rstrip("/") + settings.APP_BASE_PATH + "reset-password?" + query
            try:
                send_mail(
                    subject="بازیابی رمز عبور AI API Maker",
                    message=f"برای تنظیم رمز جدید وارد شوید:\n{url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception:
                return Response({"error": {"code": "mailer_unavailable"}}, status=503)
        response = Response({"status": "accepted"}, status=202)
        response["Cache-Control"] = "no-store"
        return response


@method_decorator(csrf_protect, name="dispatch")
class PasswordResetConfirmView(PublicAPIView):
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: OpenApiResponse(description="Password reset completed")},
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            raw_pk = force_str(urlsafe_base64_decode(data["uid"]))
            user = get_user_model().objects.get(pk=UUID(raw_pk), is_active=True)
        except (ValueError, TypeError, OverflowError, get_user_model().DoesNotExist):
            user = None
        if user is None or not default_token_generator.check_token(user, data["token"]):
            return Response({"error": {"code": "invalid_reset_token"}}, status=400)
        try:
            validate_password(data["new_password"], user)
        except DjangoValidationError as exc:
            return Response({"error": {"code": "weak_password", "details": exc.messages}}, status=400)
        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        AuthDeviceSession.objects.filter(user=user, revoked_at__isnull=True).update(
            revoked_at=timezone.now()
        )
        AuthEvent.record("password_reset", request, user=user, success=True)
        return Response({"status": "password_reset"})
