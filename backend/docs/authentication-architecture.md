# Authentication Architecture

## Overview

This application uses **RS256 (RSA Signature with SHA-256)** for JWT-based authentication. RS256 is an asymmetric algorithm that uses a private key to sign tokens and a public key to verify them, making it ideal for distributed systems where multiple services need to verify tokens without sharing signing credentials.

## Key Components

### 1. Token Generation (`scripts/generate_token.py`)

```bash
uv run scripts/generate_token.py         # user token
uv run scripts/generate_token.py admin   # admin token
```

### 2. Token Validation (`app/auth/jwt.py`)

`get_current_user()` reads the `Authorization: Bearer <token>` header, verifies the
signature with `JWT_PUBLIC_KEY`, and returns the decoded payload. Returns `401` on a
missing header, bad scheme, expired token, or invalid signature.

### 3. Permission Layers (`app/auth/permissions.py`)

- `require_user` — any authenticated user
- `require_admin` — requires `payload["role"] == "admin"`, otherwise `403`

## Route Protection Patterns

```python
# Public route
@router.get("/health")
async def health():
    return {"status": "healthy"}

# User-protected route
@router.get("/documents", response_model=list[DocumentRead])
async def get_documents(user: dict = Depends(require_user)):
    ...

# Admin-protected route
@router.delete("/documents/{document_id}")
async def delete_document(user: dict = Depends(require_admin)):
    ...
```

## Environment Configuration

```bash
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
```

Newlines must be represented as `\n` in the env var. Never commit `.env`.

## Testing with Authentication

`tests/conftest.py` provides `auth_headers` and `admin_headers` fixtures that sign a
short-lived RS256 token with `JWT_PRIVATE_KEY` from the environment.

## Troubleshooting

- **401 "Authorization header missing"** — request is missing the `Authorization` header.
- **401 "Invalid authentication scheme"** — header must be `Bearer <token>`.
- **401 "Token has expired"** — generate a new token.
- **401 "Invalid token"** — `JWT_PUBLIC_KEY` doesn't match the signing key.
- **403 "Admin access required"** — token's `role` claim isn't `admin`.
