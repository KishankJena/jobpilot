# JobPath Backend API

Production-grade FastAPI backend for JobPath SaaS platform with complete authentication system.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Async SQLAlchemy**: Asynchronous database ORM with PostgreSQL
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt-based password security with Passlib
- **Token Blacklisting**: Stateless logout with in-memory blacklist (Redis-ready)
- **CORS Support**: Configured for cross-origin requests
- **Structured Logging**: Production-ready logging configuration
- **Exception Handling**: Clean, custom exception handling
- **Dependency Injection**: FastAPI dependency injection pattern
- **Pydantic Schemas**: Request/response validation

## Architecture

The backend follows a clean, layered architecture:

```
Router → Service → Repository → Database
```

- **Router**: API endpoint definitions and request validation
- **Service**: Business logic and domain operations
- **Repository**: Data access operations
- **Database**: PostgreSQL with async SQLAlchemy

## Project Structure

```
app/
├── config/
│   ├── settings.py           # Environment and application settings
│   └── log_config.py         # Logging configuration
├── core/                     # Framework-level abstractions
│   ├── event/                # Event handlers
│   ├── model/                # Domain models
│   ├── repository/           # Base repository classes
│   └── service/              # Base service classes
├── db/
│   └── database.py           # Database engine and session management
├── dependencies/
│   └── dependency.py         # FastAPI dependency injection
├── exceptions/
│   └── exceptions.py         # Custom exceptions
├── model/
│   └── models.py             # SQLAlchemy ORM models
├── services/
│   └── auth/
│       ├── router.py         # Authentication endpoints
│       ├── schemas.py        # Pydantic request/response models
│       ├── service.py        # Authentication business logic
│       ├── repository.py     # User data access
│       └── security.py       # JWT and password utilities
├── utils/                    # Utility functions
├── middlewares/              # Custom middleware
├── lifespan/                 # Lifespan event handlers
└── main.py                   # FastAPI application entry point
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- pip or uv package manager

### Setup

1. **Clone the repository and navigate to backend directory**

```bash
cd backend/app
```

2. **Create and activate virtual environment**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using uv
uv venv
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
# Or with uv
uv pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and JWT secret:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/jobpath_db
JWT_SECRET_KEY=your-super-secret-key-make-it-strong
```

5. **Create PostgreSQL database**

```bash
createdb jobpath_db
# Or using psql
psql -U postgres -c "CREATE DATABASE jobpath_db;"
```

6. **Initialize database (create tables)**

The tables will be created automatically on application startup, or you can use Alembic migrations (optional):

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Application

### Development Mode

```bash
cd backend/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
cd backend/app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication Endpoints

### 1. Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2024-02-06T10:30:00Z"
}
```

### 2. Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_active": true
  }
}
```

### 3. Get Current User
```http
GET /auth/me
Authorization: Bearer {{ access_token }}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true
}
```

### 4. Logout
```http
POST /auth/logout
Authorization: Bearer {{ access_token }}
```

**Response (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

## Using JWT in Protected Routes

To protect routes and require authentication, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.dependencies.dependency import get_current_user

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user['email']}",
        "user_id": current_user["user_id"]
    }
```

The `current_user` will contain:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
}
```

## Security Features

### Password Hashing
- **Algorithm**: Bcrypt with 12 rounds
- **Library**: Passlib
- Passwords are never stored in plain text
- Uses constant-time comparison for verification

### JWT Tokens
- **Algorithm**: HS256
- **Secret Key**: Change `JWT_SECRET_KEY` in production
- **Expiration**: Configurable (default 30 minutes)
- **Payload**: Contains `user_id` and `email`
- **Blacklisting**: Implemented for logout (in-memory, Redis-ready)

### Token Blacklist
- In-memory set for quick access
- Production-ready architecture for Redis migration
- Prevents token reuse after logout

## Configuration

### Settings (app/config/settings.py)

All configuration is managed through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | JobPath | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `DEBUG` | False | Debug mode flag |
| `DATABASE_URL` | postgresql://... | PostgreSQL connection string |
| `JWT_SECRET_KEY` | your-secret-key | JWT signing secret (CHANGE IN PRODUCTION) |
| `JWT_ALGORITHM` | HS256 | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |
| `BCRYPT_ROUNDS` | 12 | Bcrypt hashing rounds |
| `CORS_ORIGINS` | localhost:3000,8000 | Allowed CORS origins |
| `LOG_LEVEL` | INFO | Logging level |

## Database

### Models

#### User Model
- `id` (UUID, PK): Unique user identifier
- `email` (String, Unique, Indexed): User email address
- `password_hash` (String): Bcrypt hashed password
- `is_active` (Boolean, Default=True): Account status
- `created_at` (DateTime, UTC): Creation timestamp
- `updated_at` (DateTime, UTC): Last update timestamp

## Error Handling

The API returns standardized error responses:

```json
{
  "error": "invalid_credentials",
  "detail": {
    "message": "Invalid email or password"
  },
  "status_code": 401
}
```

### Common Status Codes
- `201`: Created (successful signup)
- `200`: OK (success)
- `400`: Bad Request (validation error)
- `401`: Unauthorized (auth failure)
- `409`: Conflict (duplicate email)
- `500`: Internal Server Error

## Testing

Run tests with pytest:

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Verbose output
pytest -v

# Specific test file
pytest tests/test_auth.py
```

## Production Deployment

### Before Deploying

1. **Change JWT Secret**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update `JWT_SECRET_KEY` in `.env`

2. **Use Strong Database Password**
   Ensure `DATABASE_URL` uses a strong password

3. **Set DEBUG=False**
   ```env
   DEBUG=False
   ```

4. **Configure CORS properly**
   ```env
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

5. **Setup proper logging**
   ```env
   LOG_LEVEL=WARNING
   ```

6. **Use Redis for token blacklist** (optional)
   Migrate from in-memory set to Redis in `security.py`

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t jobpath-api .
docker run -p 8000:8000 --env-file .env jobpath-api
```

## Troubleshooting

### Database Connection Error
```
postgresql.asyncpg.UnsupportedServerVersionError
```
Ensure PostgreSQL 13+ is running and `DATABASE_URL` is correct.

### JWT Secret Warning
```
JWT_SECRET_KEY not set or insecure
```
Generate a secure secret key and update `.env`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Issues
If frontend requests are blocked:
1. Check `CORS_ORIGINS` includes your frontend URL
2. Ensure `CORS_CREDENTIALS=True` if using cookies
3. Clear browser cache and try again

## Performance Optimization

1. **Database Connection Pooling**
   - `DB_POOL_SIZE`: 20 (connections)
   - `DB_MAX_OVERFLOW`: 10 (extra connections)
   - Adjust based on expected concurrent users

2. **Async/Await**
   - All operations are async for non-blocking I/O
   - Enables handling thousands of concurrent requests

3. **Caching**
   - Implement Redis caching for frequently accessed data
   - Cache JWT blacklist checks (already optimized with set lookups)

## Future Enhancements

- [ ] Email verification
- [ ] Password reset flow
- [ ] Refresh token implementation
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC)
- [ ] Audit logging
- [ ] Rate limiting
- [ ] API key authentication
- [ ] OAuth2 / Social login
- [ ] Redis integration for token blacklist

## License

Proprietary - JobPath Inc.

## Support

For issues, questions, or contributions, contact the development team.
