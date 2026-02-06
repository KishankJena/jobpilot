"""
API routes for authentication endpoints.
"""
from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.services.auth.service import AuthService
from app.services.auth.security import oauth2_scheme, extract_token_from_header
from app.services.auth.schemas import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    ErrorResponse,
)
from app.exceptions.exceptions import JobPathException

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account with email and password",
)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SignupResponse:
    """Register a new user.
    
    Args:
        request: Signup request with email and password
        session: Database session dependency
        
    Returns:
        Created user information
        
    Raises:
        DuplicateEmailException: If email already exists
        ValidationException: If input validation fails
    """
    try:
        auth_service = AuthService(session)
        user_data = await auth_service.signup(
            email=request.email,
            password=request.password,
        )
        return SignupResponse(**user_data)
    except JobPathException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.detail.get("error", "signup_error"),
                "detail": e.detail,
                "status_code": e.status_code,
            },
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=200,
    summary="Authenticate user",
    description="Login with email and password to receive JWT access token",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    """Authenticate user and generate JWT token.
    
    Args:
        request: Login request with email and password
        session: Database session dependency
        
    Returns:
        Access token and user information
        
    Raises:
        InvalidCredentialsException: If email or password is incorrect
    """
    try:
        auth_service = AuthService(session)
        token_data = await auth_service.login(
            email=request.email,
            password=request.password,
        )
        return LoginResponse(**token_data)
    except JobPathException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.detail.get("error", "login_error"),
                "detail": e.detail,
                "status_code": e.status_code,
            },
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=200,
    summary="Logout user",
    description="Logout by invalidating the JWT token",
)
async def logout(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
) -> LogoutResponse:
    """Logout user by blacklisting JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        session: Database session dependency
        
    Returns:
        Logout confirmation
        
    Raises:
        InvalidTokenException: If token is invalid or missing
    """
    try:
        # Extract token from header
        token = extract_token_from_header(authorization)
        
        auth_service = AuthService(session)
        result = await auth_service.logout(token)
        return LogoutResponse(**result)
    except JobPathException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.detail.get("error", "logout_error"),
                "detail": e.detail,
                "status_code": e.status_code,
            },
        )


@router.get(
    "/me",
    response_model=dict,
    status_code=200,
    summary="Get current user",
    description="Get information about the authenticated user",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def get_current_user(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get current authenticated user information.
    
    Args:
        authorization: Authorization header with Bearer token
        session: Database session dependency
        
    Returns:
        Current user information
        
    Raises:
        InvalidTokenException: If token is invalid or expired
    """
    try:
        # Extract token from header
        token = extract_token_from_header(authorization)
        
        auth_service = AuthService(session)
        user = await auth_service.get_current_user(token)
        return user
    except JobPathException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.detail.get("error", "auth_error"),
                "detail": e.detail,
                "status_code": e.status_code,
            },
        )
