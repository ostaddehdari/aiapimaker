"""Stage 04 isolated API smoke tests. No live provider or VPS access."""

from uuid import uuid4

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings


class ProbeTests(SimpleTestCase):
    def test_health_is_public_and_versioned(self):
        response = self.client.get(settings.API_BASE_PATH + "health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "aiapimaker-django")
        self.assertTrue(response.headers.get("X-Request-ID"))

    def test_liveness_is_public(self):
        response = self.client.get(settings.API_BASE_PATH + "live/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "alive")

    def test_request_id_accepts_only_uuid(self):
        known = str(uuid4())
        response = self.client.get(
            settings.API_BASE_PATH + "health/", HTTP_X_REQUEST_ID=known
        )
        self.assertEqual(response.headers["X-Request-ID"], known)
        response = self.client.get(
            settings.API_BASE_PATH + "health/", HTTP_X_REQUEST_ID="bad\nrequest"
        )
        self.assertNotEqual(response.headers["X-Request-ID"], "bad\nrequest")

    def test_schema_is_json(self):
        response = self.client.get(settings.API_BASE_PATH + "schema/?format=json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("openapi", response.json())

    @override_settings(DEBUG=False)
    def test_unknown_api_path_does_not_return_html(self):
        response = self.client.get(settings.API_BASE_PATH + "does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["error"]["code"], "not_found")


class DatabaseProbeTests(TestCase):
    def test_readiness_checks_test_database(self):
        response = self.client.get(settings.API_BASE_PATH + "ready/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ready")
