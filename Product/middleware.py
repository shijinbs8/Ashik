import logging

logger = logging.getLogger(__name__)

class LogExceptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error("Unhandled exception", exc_info=True)
            raise  # re-raise so Django can handle it
        return response

