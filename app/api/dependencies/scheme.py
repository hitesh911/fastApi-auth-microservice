from fastapi import Header , HTTPException,status
from app.api.models.common import Token

class TokenValidationScheme:
    def __init__(self, token_type: str = "Bearer"):
        self.token_type = token_type

    def __call__(self, Authorization: str = Header()):
        try:
            token_type, token = Authorization.split(" ")
            if token_type.lower() != self.token_type.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return Token(access_token=token, token_type=token_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
