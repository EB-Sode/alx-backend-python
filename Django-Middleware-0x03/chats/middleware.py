import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware that logs each request with user and path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user (handle anonymous users gracefully)
        user = request.user if request.user.is_authenticated else "Anonymous"

        # Log the request info
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Continue the request/response cycle
        response = self.get_response(request)
        return response
