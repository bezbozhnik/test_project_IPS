from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated, PermissionDenied


class AuthRequired(NotAuthenticated):
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class AuthorizationFailed(PermissionDenied):
    DETAIL = ErrorCode.AUTHORIZATION_FAILED


class InvalidCredentials(NotAuthenticated):
    DETAIL = ErrorCode.INVALID_CREDENTIALS


class EmailTaken(BadRequest):
    DETAIL = ErrorCode.EMAIL_TAKEN


class InvalidPassoword(BadRequest):
    DETAIL = ErrorCode.INVALID_PASSWORD
