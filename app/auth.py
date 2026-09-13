from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


# Password hashing
password_hash = PasswordHash.recommended()


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_password(password: str) -> str:
    """
    Convert plain password into a secure hashed password.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Check whether the entered password matches
    the stored hashed password.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# =========================================================
# JWT TOKEN
# =========================================================

def create_access_token(
    username: str,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create JWT access token for authenticated user.
    """

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": username,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token