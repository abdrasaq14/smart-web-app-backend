from rest_framework import status
from rest_framework.exceptions import APIException, _get_error_details


class GenericErrorException(APIException):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A server error occurred."
    default_code = "error"

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.status_code = status_code or self.status_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = {"detail": detail}
        self.detail = _get_error_details(detail, code)
