
from rest_framework.response import Response as DRFResponse

def Response(success=True, status_code=200, message="Request successful", data=None):
    """
    Utility function to generate a custom API response.

    Args:
        success (bool): Indicates if the request was successful.
        status_code (int): The HTTP status code.
        message (str): A message to describe the response.
        data (dict): The data payload to include in the response.

    Returns:
        Response: A Django REST Framework Response object with the custom structure.
    """
    response = {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data if data is not None else [],
    }
    return DRFResponse(response, status=status_code)