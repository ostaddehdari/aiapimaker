"""First-party Django session routes (provider OAuth is a separate concern)."""

from django.urls import path

from .views import (
    ChangePasswordView,
    CsrfBootstrap,
    DeviceSessionsView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RevokeDeviceView,
)

urlpatterns = [
    path("csrf/", CsrfBootstrap.as_view(), name="auth-csrf"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("sessions/", DeviceSessionsView.as_view(), name="auth-sessions"),
    path("sessions/revoke/", RevokeDeviceView.as_view(), name="auth-session-revoke"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="auth-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-reset-confirm"),
]
