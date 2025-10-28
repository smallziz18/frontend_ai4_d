from typing import Any, Callable, Coroutine

from fastapi import FastAPI, status, HTTPException

from sqlalchemy.exc import NoResultFound
from starlette.requests import Request
from starlette.responses import JSONResponse


class DefaultException(Exception):
    """
    this the base class for all exceptions
"""
    pass


class InvalidToken(DefaultException):
    """
    User has invalid token
"""
    pass



class ExpiredToken(DefaultException):
    """
    User has provided an expired token
"""
    pass

class RevokedToken(DefaultException):
    """
    User token has been revoked
"""
    pass

class RefreshTokenRequired(DefaultException):
    """
    user has to provide a refresh token
    """
    pass

class AccessTokenRequired(DefaultException):
    """
    user has to provide an access token
    """
    pass

class UserNotFound(DefaultException):
    """
    User not found
    """
    pass

class ProfileNotFound(DefaultException):
    """
    Profile not found
    """
    pass

class Forbidden(DefaultException):
    """
    User has been forbidden to access this page
    """

class UserAlreadyExists(DefaultException):
    """
    User already exists
    """
    pass

# src/error.py (ajouter cette exception)
class EmailNotVerified(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and verify your account."
        )



def create_error_handler(status_code: int, initial_detail: Any) -> Callable[
    [Request, Exception], Coroutine[Any, Any, JSONResponse]]:
    async def exception_handler(request: Request, exception: Exception) -> JSONResponse:
        return JSONResponse(
            content=initial_detail,
            status_code=status_code,
        )

    return exception_handler



def register_error_handler(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_error_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "User already exists",
                "error_code": "user_exists"
            }
        )
    )

    app.add_exception_handler(
        InvalidToken,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token provided",
                "error_code": "invalid_token"
            }
        )
    )

    app.add_exception_handler(
        ExpiredToken,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has expired",
                "error_code": "expired_token"
            }
        )
    )

    app.add_exception_handler(
        RevokedToken,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked",
                "error_code": "revoked_token"
            }
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Refresh token is required",
                "error_code": "refresh_token_required"
            }
        )
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_error_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token is required",
                "error_code": "access_token_required"
            }
        )
    )

    app.add_exception_handler(
        UserNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )

    app.add_exception_handler(
        ProfileNotFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Profile not found",
                "error_code": "profile_not_found"
            }
        )
    )

    app.add_exception_handler(
        Forbidden,
        create_error_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Access forbidden",
                "error_code": "forbidden"
            }
        )
    )

    # Handle SQLAlchemy NoResultFound exception
    app.add_exception_handler(
        NoResultFound,
        create_error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Resource not found",
                "error_code": "not_found"
            }
        )
    )