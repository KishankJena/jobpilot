"""
Custom exceptions for JobPath backend.
"""
from typing import Optional


class JobPathException(Exception):
    """Base exception for JobPath application."""
    
    def __init__(self, message: str, status_code: int = 500, detail: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class AuthenticationException(JobPathException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", detail: Optional[dict] = None):
        super().__init__(message, status_code=401, detail=detail)


class InvalidCredentialsException(AuthenticationException):
    """Raised when credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, detail={"error": "invalid_credentials"})


class UserNotFoundException(AuthenticationException):
    """Raised when user is not found."""
    
    def __init__(self, message: str = "User not found"):
        super().__init__(message, detail={"error": "user_not_found"})


class DuplicateEmailException(JobPathException):
    """Raised when email is already registered."""
    
    def __init__(self, message: str = "Email already registered"):
        super().__init__(message, status_code=409, detail={"error": "email_exists"})


class TokenException(AuthenticationException):
    """Raised when token validation fails."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, detail={"error": "invalid_token"})


class TokenExpiredException(TokenException):
    """Raised when token is expired."""
    
    def __init__(self, message: str = "Token expired"):
        super().__init__(message, detail={"error": "token_expired"})


class InvalidTokenException(TokenException):
    """Raised when token format is invalid."""
    
    def __init__(self, message: str = "Invalid token format"):
        super().__init__(message, detail={"error": "invalid_token_format"})


class AuthorizationException(JobPathException):
    """Raised when user is not authorized."""
    
    def __init__(self, message: str = "Not authorized", detail: Optional[dict] = None):
        super().__init__(message, status_code=403, detail=detail or {"error": "not_authorized"})


class ValidationException(JobPathException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation failed", detail: Optional[dict] = None):
        super().__init__(message, status_code=422, detail=detail or {"error": "validation_error"})


class DatabaseException(JobPathException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status_code=500, detail={"error": "database_error"})
