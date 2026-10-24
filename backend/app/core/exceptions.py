from fastapi import HTTPException


class AppError(HTTPException):
    """A user-facing API error with a stable HTTP status."""


def bad_request(detail: str) -> AppError:
    return AppError(status_code=400, detail=detail)
