import os

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

SUPER_SECRET_TOKEN = os.getenv("SUPER_SECRET_TOKEN", "secret-api-token")


def verify_auth_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    if credentials.scheme != "Bearer" or credentials.credentials != SUPER_SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
