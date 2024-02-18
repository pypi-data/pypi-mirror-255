"""Security module for JWT validation."""

import logging
from fastapi import Request, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
from mumichaspy.fastapi_jwt_chassis.config import config

logger = logging.getLogger(__name__)


def validate_and_decode_token(
    encoded_token: str,
    public_key: config.public_key,
    issuer: config.jwt_issuer,
    algorithms: None,
) -> dict:
    """Decode JWT if validates."""
    if algorithms is None or len(algorithms) == 0:
        algorithms = [config.jwt_algorithm]

    decoded_token = {}
    try:
        decoded_token = jwt.decode(
            encoded_token, public_key, issuer=issuer, algorithms=algorithms
        )
    except Exception as exc:
        raise_and_log_error(
            logger,
            status.HTTP_403_FORBIDDEN,
            "Could not decode JWT",
            f"Could not decode JWT: {exc}",
        )
    return decoded_token


class JWTBearer(HTTPBearer):  # pylint: disable=too-few-public-methods
    """HTTPBearer implementation for JWT validation."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # Get credentials from header
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        # Check credential scheme
        if not credentials.scheme == "Bearer":
            raise_and_log_error(
                logger, status.HTTP_403_FORBIDDEN, "Invalid authentication scheme"
            )

        # Check if token is valid
        decoded_jwt = validate_and_decode_token(
            encoded_token=credentials.credentials,
            public_key=config.public_key,
            issuer=config.jwt_issuer,
            algorithms=[config.jwt_algorithm],
        )

        # Check issuer
        if decoded_jwt["iss"] != config.jwt_issuer:
            raise_and_log_error(
                logger, status.HTTP_403_FORBIDDEN, "Invalid JWT issuer."
            )

        # Return decoded JWT
        return decoded_jwt


class JWTBearerAdmin(JWTBearer):  # pylint: disable=too-few-public-methods
    """HTTPBearer implementation for JWT validation."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        decoded_jwt = await super().__call__(request)
        # Check admin role
        if "ADMIN" not in decoded_jwt["roles"]:
            raise_and_log_error(
                logger, status.HTTP_403_FORBIDDEN, "Only admins can perform this action"
            )
        return decoded_jwt


def raise_and_log_error(
    my_logger, status_code: int, message: str, message_to_log: str = None
):
    """Raises HTTPException and logs an error."""

    if message_to_log is None:
        message_to_log = message

    my_logger.error(message_to_log)
    raise HTTPException(status_code, message)
