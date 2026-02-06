"""
Security utilities for authentication including JWT and password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.exceptions.exceptions import InvalidTokenException, TokenExpiredException


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Token blacklist (in-memory, Redis-ready)
token_blacklist: set = set()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Payload data to encode in token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        InvalidTokenException: If token is invalid or malformed
        TokenExpiredException: If token is expired
    """
    # Check if token is blacklisted
    if token in token_blacklist:
        raise InvalidTokenException("Token has been revoked")
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        if "expired" in str(e).lower():
            raise TokenExpiredException("Token has expired")
        raise InvalidTokenException(f"Invalid token: {str(e)}")


def add_token_to_blacklist(token: str) -> None:
    """Add a token to the blacklist (logout).
    
    Args:
        token: JWT token to blacklist
    """
    token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted.
    
    Args:
        token: JWT token to check
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    return token in token_blacklist


def extract_token_from_header(auth_header: str) -> str:
    """Extract token from Authorization header.
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        Token string
        
    Raises:
        InvalidTokenException: If header format is invalid
    """
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenException("Invalid authorization header format")
    
    return parts[1]
