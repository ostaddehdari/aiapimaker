"""API root path is configured by environment, not a hardcoded public hostname."""

from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_not_found(request, exception=None):
    if request.path.startswith(settings.API_BASE_PATH):
        return JsonResponse(
            {
                "error": {
                    "code": "not_found",
                    "message": "Resource not found",
                    "request_id": getattr(request, "request_id", None),
                }
            },
            status=404,
        )
    return JsonResponse({"error": {"code": "not_found"}}, status=404)


def api_error(request):
    return JsonResponse(
        {
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
                "request_id": getattr(request, "request_id", None),
            }
        },
        status=500,
    )


prefix = settings.API_BASE_PATH.lstrip("/")
urlpatterns = [
    path(prefix, include("apps.core.urls")),
    path(prefix + "auth/", include("apps.users.urls")), 
    path(prefix + "schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        prefix + "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

handler404 = api_not_found
handler500 = api_error
