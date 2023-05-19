import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException

from .config import Settings


# Auxiliary class for auth work
class Auth:
    hasher = CryptContext(schemes="bcrypt")
    secret = Settings().secret_key

    # Create token
    def encode_token(self, username: str) -> str:
        payload = {
            'exp': int(datetime.timestamp(datetime.utcnow() + timedelta(days=0, minutes=300))),
            'iat': int(datetime.timestamp(datetime.utcnow())),
            'scope': 'access_token',
            'data': username
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    # Check token
    def decode_token(self, access_token: str) -> str:
        try:
            payload = jwt.decode(access_token, self.secret, algorithms="HS256")
            if payload["scope"] == "access_token":
                return payload["data"]
            raise HTTPException(status_code=401, detail="Scope for the token is invalid.")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token.")
