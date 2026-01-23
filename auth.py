from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth
import logging
import os

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        if os.path.exists(settings.firebase_credentials_path):
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            logger.warning(
                f"Firebase credentials file not found at {settings.firebase_credentials_path}")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")


security = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Verify Firebase ID token and return user info.

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        dict: Decoded token containing user info (uid, email, etc.)

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = credentials.credentials

    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(token)

        # Extract user info
        user_info = {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
        }

        return user_info

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired. Please login again."
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked. Please login again."
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


def get_current_user(user_info: dict = Security(verify_firebase_token)) -> dict:
    """
    Dependency to get current authenticated user.
    Use this in route handlers to protect endpoints.
    """
    return user_info
