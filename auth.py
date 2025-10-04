from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt, JWTError

SECRET_KEY = "CHANGE_ME_______STRONG_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    """Hash plain password using bcrypt."""
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """Check if plain password matches hashed one."""
    return pwd_context.verify(raw, hashed)


def create_access_token(sub: str, role: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """Generate JWT access token."""
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token and return its payload."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
