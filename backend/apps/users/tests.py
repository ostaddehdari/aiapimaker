"""Stage 07 first-party session/auth security regression tests."""

import re
import uuid
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.utils import timezone

from .security_models import AuthDeviceSession, AuthEvent, LoginThrottle


class AuthFlowTests(TestCase):
    def setUp(self):
        self.base = settings.API_BASE_PATH + "auth/"
        self.user_password = "Testing-Strong-" + uuid.uuid4().hex
        self.new_password = "Changed-Strong-" + uuid.uuid4().hex
        self.user = get_user_model().objects.create_user(
            username="demo_user", email="demo@example.test", password=self.user_password
        )
        self.client = Client(enforce_csrf_checks=True)
        self.csrf = self._csrf(self.client)

    def _csrf(self, client):
        response = client.get(self.base + "csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrf_token", response.json())
        return response.json()["csrf_token"]

    def _post(self, suffix, payload, *, client=None, csrf=None):
        import json

        client = client or self.client
        return client.post(
            self.base + suffix,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf if csrf is not None else self.csrf,
        )

    def _login(self, *, client=None, csrf=None):
        return self._post(
            "login/",
            {"username": self.user.username, "password": self.user_password},
            client=client,
            csrf=csrf,
        )

    def test_csrf_is_required_even_for_anonymous_login(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            self.base + "login/",
            data='{"username":"demo_user","password":"anything"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["error"]["code"], "csrf_failed")

    def test_login_me_logout_and_secure_cookie_attributes(self):
        self.assertEqual(self.client.get(self.base + "me/").status_code, 403)
        login = self._login()
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["user"]["role"], "user")
        self.assertTrue(login.cookies[settings.SESSION_COOKIE_NAME]["httponly"])
        self.assertEqual(login.cookies[settings.SESSION_COOKIE_NAME]["samesite"], "Lax")
        self.assertEqual(login.cookies[settings.SESSION_COOKIE_NAME]["path"], settings.APP_BASE_PATH)
        self.assertEqual(self.client.get(self.base + "me/").status_code, 200)
        self.assertEqual(self.client.get(self.base + "sessions/").json()["sessions"][0]["current"], True)
        self.assertEqual(self._post("logout/", {}).status_code, 200)
        self.assertEqual(self.client.get(self.base + "me/").status_code, 403)
        self.assertEqual(AuthDeviceSession.objects.filter(revoked_at__isnull=True).count(), 0)

    def test_wrong_password_lockout_is_generic_and_audited_without_plain_identifier(self):
        for _ in range(3):
            response = self._post("login/", {"username": "demo_user", "password": "incorrect"})
            self.assertEqual(response.status_code, 401)
        response = self._login()
        self.assertEqual(response.status_code, 429)
        self.assertTrue(LoginThrottle.objects.exists())
        self.assertEqual(AuthEvent.objects.filter(event="login_failed").count(), 3)
        self.assertFalse(AuthEvent.objects.filter(identifier_hash__contains="demo_user").exists())

    def test_revoked_device_is_denied_on_next_request(self):
        self.assertEqual(self._login().status_code, 200)
        other = Client(enforce_csrf_checks=True)
        csrf_other = self._csrf(other)
        second = self._login(client=other, csrf=csrf_other)
        self.assertEqual(second.status_code, 200)
        revoked = self._post(
            "sessions/revoke/", {"session_id": second.json()["session_id"]}
        )
        self.assertEqual(revoked.status_code, 200)
        self.assertEqual(other.get(self.base + "me/").status_code, 401)
        self.assertEqual(self.client.get(self.base + "me/").status_code, 200)

    def test_own_device_cannot_revoke_another_users_device(self):
        other = get_user_model().objects.create_user(
            username="other_user", password="Other-Strong-" + uuid.uuid4().hex
        )
        self.assertEqual(self._login().status_code, 200)
        alien = AuthDeviceSession.objects.create(
            user=other, session_hash="f" * 64,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        response = self._post("sessions/revoke/", {"session_id": str(alien.pk)})
        self.assertEqual(response.status_code, 404)
        alien.refresh_from_db()
        self.assertIsNone(alien.revoked_at)

    def test_session_expiration_denies_access(self):
        response = self._login()
        self.assertEqual(response.status_code, 200)
        AuthDeviceSession.objects.filter(pk=response.json()["session_id"]).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(self.client.get(self.base + "me/").status_code, 401)

    def test_password_change_preserves_current_device_but_revokes_others(self):
        self.assertEqual(self._login().status_code, 200)
        other = Client(enforce_csrf_checks=True)
        other_csrf = self._csrf(other)
        self.assertEqual(self._login(client=other, csrf=other_csrf).status_code, 200)
        response = self._post(
            "change-password/",
            {"current_password": self.user_password, "new_password": self.new_password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(self.base + "me/").status_code, 200)
        self.assertEqual(other.get(self.base + "me/").status_code, 401)

    def test_password_reset_is_non_enumerating_and_invalidates_devices(self):
        self.assertEqual(self._login().status_code, 200)
        unknown = self._post("password-reset/request/", {"email": "unknown@example.test"})
        self.assertEqual(unknown.status_code, 202)
        self.assertEqual(len(mail.outbox), 0)
        sent = self._post("password-reset/request/", {"email": "demo@example.test"})
        self.assertEqual(sent.status_code, 202)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r"https?://[^\s]+", mail.outbox[0].body)
        self.assertIsNotNone(match)
        params = parse_qs(urlparse(match.group()).query)
        response = self._post(
            "password-reset/confirm/",
            {"uid": params["uid"][0], "token": params["token"][0], "new_password": self.new_password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(self.base + "me/").status_code, 401)
        repeated = self._post(
            "password-reset/confirm/",
            {"uid": params["uid"][0], "token": params["token"][0], "new_password": self.new_password},
        )
        self.assertEqual(repeated.status_code, 400)

    def test_admin_role_requires_staff_flag(self):
        self.user.platform_role = "admin"
        self.user.save(update_fields=["platform_role"])
        self.assertEqual(self._login().json()["user"]["role"], "user")
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        self.assertEqual(self.client.get(self.base + "me/").json()["user"]["role"], "admin")

    def test_openapi_schema_lists_login_and_recovery(self):
        schema = self.client.get(settings.API_BASE_PATH + "schema/?format=json")
        self.assertEqual(schema.status_code, 200)
        paths = schema.json()["paths"]
        self.assertIn(self.base + "login/", paths)
        self.assertIn(self.base + "password-reset/request/", paths)
