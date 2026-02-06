"""
Sample test file for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from app.services.auth.security import hash_password
from app.model.models import User


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, test_db):
    """Test successful user signup."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_db):
    """Test signup with duplicate email."""
    # Create first user
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    # Try to create user with same email
    response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert data["detail"]["error"] == "email_exists"


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient):
    """Test signup with invalid email."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "invalid-email",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    """Test signup with weak password."""
    response = await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "weak",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_db):
    """Test successful login."""
    # First signup
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    # Then login
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_db):
    """Test login with wrong password."""
    # First signup
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    # Try login with wrong password
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    response = await client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_db):
    """Test getting current user from token."""
    # Signup and login
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, test_db):
    """Test successful logout."""
    # Signup and login
    await client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
        },
    )
    token = login_response.json()["access_token"]
    
    # Logout
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"
