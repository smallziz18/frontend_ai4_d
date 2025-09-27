from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Request, HTTPException,status


from utils import decode_token


class AccessToken(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request)-> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        if creds:
            token = creds.credentials
            token_data = decode_token(token)
            if not self.is_token_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired credentials",
                )
            if token_data["refresh_token"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Please refresh your access token",
                )
        return creds
    @staticmethod
    def is_token_valid(self, token:str)->bool:
        token_data = decode_token(token)
        if token_data is None:
            return True
        return False


