# JobPath Backend API - Quick Start Guide

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend/app
pip install -r requirements.txt
```

### 2. Setup PostgreSQL (Using Docker)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on `localhost:5432`
- PgAdmin on `http://localhost:5050` (admin@jobpath.com / admin)

### 3. Configure Environment

Copy and edit `.env`:
```bash
cp .env.example .env
```

Default development credentials are already in `.env`.

### 4. Run Application

```bash
cd backend/app
python -m uvicorn app.main:app --reload
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

---

## API Usage Examples

### 1. Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from response.

### 3. Get Current User
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Project Structure

```
backend/app/
├── app/
│   ├── config/              # Settings and logging
│   ├── core/                # Base classes and abstractions
│   ├── db/                  # Database connection
│   ├── dependencies/        # Dependency injection
│   ├── exceptions/          # Custom exceptions
│   ├── model/               # SQLAlchemy models
│   ├── services/auth/       # Authentication logic
│   ├── utils/               # Utilities
│   ├── main.py              # FastAPI app
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (dev)
├── docker-compose.yml       # PostgreSQL setup
└── README.md               # Full documentation
```

---

## Key Features

✅ **Complete Authentication System**
- Signup with email validation
- Login with JWT tokens
- Logout with token blacklisting
- Password hashing with bcrypt

✅ **Clean Architecture**
- Router → Service → Repository → Database
- Dependency injection pattern
- Fully async/await

✅ **Security**
- JWT token-based authentication
- Bcrypt password hashing (12 rounds)
- Token validation and expiration
- In-memory token blacklist (Redis-ready)

✅ **Production Ready**
- Structured error handling
- Pydantic validation
- CORS support
- Logging configuration
- Type hints throughout

---

## Testing

```bash
pytest tests/
pytest tests/test_auth.py -v
pytest --cov=app
```

---

## Extending the Backend

### Add a New Protected Route

```python
# In app/services/myfeature/router.py
from fastapi import APIRouter, Depends
from app.dependencies.dependency import get_current_user

router = APIRouter(prefix="/api", tags=["MyFeature"])

@router.get("/protected-endpoint")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['email']}"}
```

### Register in Main App

```python
# In app/main.py
from app.services.myfeature.router import router as myfeature_router
app.include_router(myfeature_router)
```

---

## Troubleshooting

**PostgreSQL connection error:**
- Check docker: `docker ps`
- Start with: `docker-compose up -d`

**JWT_SECRET_KEY warning:**
- Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Update `.env` with the generated key

**Port 5432 already in use:**
- Change port in `.env` or `docker-compose.yml`

---

## Next Steps

1. Implement additional services using the same pattern
2. Add database migrations with Alembic
3. Setup Redis for production token blacklist
4. Configure email verification
5. Add refresh token functionality

See [README.md](README.md) for comprehensive documentation.
