import os

from fastapi import HTTPException
from starlette import status

admin_token = os.getenv("CHATMANIP_ADMIN_TOKEN")


async def check_authentication(token: str):
    if not token == admin_token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        raise credentials_exception
