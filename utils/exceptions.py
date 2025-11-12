# utils/exceptions.py
# import logging
from rest_framework.views import exception_handler
from utils.helpers import Response
from django.db import DatabaseError

# logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Use DRF's default exception handler first
    response = exception_handler(exc, context)
    view = context.get('view', None)

    if response is not None:
        # logger.warning(f"Handled Exception in {view}: {exc}")
        data = response.data
        if isinstance(data, dict):
            message = data.get('detail', str(exc))
            errors = {k: v for k, v in data.items() if k != 'detail'}
        elif isinstance(data, list):
        # For list errors (nested serializer)
            message = "Validation error"
            errors = data
        else:
            message = str(exc)
            errors = {}
    return Response(
        success=False,
        status=response.status_code,
        message=message,
        errors=errors
    )

    # Unhandled exceptions (e.g. DB errors)
    # logger.error(f"Unhandled Exception in {view}: {exc}", exc_info=True)
    if isinstance(exc, DatabaseError):
        message = "Database error occurred. Please try again later."
    else:
        message = "Something went wrong. Please contact support."

    return Response(
        success=False,
        status=500,
        message=message,
        errors={'detail': str(exc)}
    )
