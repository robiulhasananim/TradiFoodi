from rest_framework.response import Response as DRFResponse

def Response(success=True, status=200, message="Request successful", data=None, errors=None, meta=None):
    """
    Custom API response for DRF with meta, with status inside JSON.

    Args:
        success (bool): Indicates if request was successful.
        status (int): HTTP status code (also included in JSON).
        message (str): Human-readable message describing the response.
        data (dict or list): The main payload data of the response.
        errors (dict): Validation or runtime errors.
        meta (dict): Metadata like pagination info.

    Returns:
        DRF Response object with consistent API structure.
    """
    response = {
        "success": success,
        "status": status,
        "message": message,
        "data": data if data is not None else {},
    }

    if errors is not None:
        response["errors"] = errors
    
    if meta is not None:
        response["meta"] = meta

    return DRFResponse(response, status=status)
