from fastapi import HTTPException
from starlette import status


async def check_authentication(token: str):
    if not token == "1234":
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        raise credentials_exception
