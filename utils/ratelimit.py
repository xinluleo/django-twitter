from rest_framework.views import exception_handler as drf_exception_handler
from django_ratelimit.exceptions import Ratelimited


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, Ratelimited):
        response.data = {
            'error': 'too many requests',
            'message': 'You have exceeded the limit of requests in a given time frame.'
        }
        response.status_code = 429

    return response
