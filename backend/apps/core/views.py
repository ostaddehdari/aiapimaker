"""Minimal liveness/readiness endpoints with no credential exposure."""

from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class PublicProbe(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []


class LivenessView(PublicProbe):
    @extend_schema(responses={200: OpenApiResponse(description="Process is running")})
    def get(self, request):
        return Response({"status": "alive", "service": "aiapimaker-django"})


class HealthView(PublicProbe):
    @extend_schema(responses={200: OpenApiResponse(description="Basic service health")})
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "aiapimaker-django",
                "version": "0.1.0-dev",
            }
        )


class ReadinessView(PublicProbe):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Database available"),
            503: OpenApiResponse(description="Database unavailable"),
        }
    )
    def get(self, request):
        try:
            connection.ensure_connection()
            ready = connection.is_usable()
        except Exception:
            # Never surface SQL errors, usernames or private connection strings.
            ready = False
        code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response({"status": "ready" if ready else "unavailable"}, status=code)
