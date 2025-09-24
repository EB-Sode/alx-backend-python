from datetime import datetime
import logging
from rest_framework.settings import api_settings
from django.http import HttpResponseForbidden
from datetime import datetime, timedelta

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


class OffensiveLanguageMiddleware:
    """
    Middleware that limits number of chat messages per IP.
    Allows max 5 messages per minute per IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Store request counts per IP: {ip: [timestamps]}
        self.request_logs = {}

    def __call__(self, request):
        ip = self.get_client_ip(request)
        now = datetime.now()

        # Track only POST requests (messages)
        if request.method == "POST" and "/messages/" in request.path:
            # Initialize log for this IP
            if ip not in self.request_logs:
                self.request_logs[ip] = []

            # Remove timestamps older than 1 minute
            self.request_logs[ip] = [
                ts for ts in self.request_logs[ip]
                if now - ts < timedelta(minutes=1)
            ]

            # Check if user exceeded limit
            if len(self.request_logs[ip]) >= 5:
                logger.warning(
                    f"{now} - BLOCKED: IP {ip} exceeded 5 messages/min on {request.path}"
                )
                return HttpResponseForbidden(
                    "❌ Rate limit exceeded: Max 5 messages per minute."
                )

            # Log this request
            self.request_logs[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
