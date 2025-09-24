from datetime import datetime
import logging
from rest_framework.settings import api_settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = "Anonymous"

        # Try DRF authentication classes
        for authenticator in api_settings.DEFAULT_AUTHENTICATION_CLASSES:
            auth = authenticator()
            try:
                auth_result = auth.authenticate(request)
                if auth_result is not None:
                    user, _ = auth_result
                    break
            except Exception:
                pass  # Ignore errors, keep user as Anonymous

        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Restrict access to the site outside allowed hours (6PM - 9PM).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current server time (24-hour format)
        now = datetime.now().time()
        start_time = datetime.strptime("18:00", "%H:%M").time()  # 6PM
        end_time = datetime.strptime("21:00", "%H:%M").time()    # 9PM

        # If current time is outside allowed hours, return 403 Forbidden
        if not (start_time <= now <= end_time):
            return HttpResponseForbidden("Allowed only between 6PM and 9PM.")

        # Otherwise continue
        response = self.get_response(request)
        return response
