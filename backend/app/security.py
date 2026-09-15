import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv()

jwt_secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256") # duplicating argument as fallback
access_token_expires = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "60"))


if not jwt_secret_key:
    raise RuntimeError("JWT_SECRET_KEY is not set")


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # deprecated="auto" - auto change outdated hash 



"""------------------------------------HASHING------------------------------------"""

def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)



"""------------------------------------TOKEN------------------------------------"""

def create_access_token(subject: str, user_id: int, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=access_token_expires)

    payload = {
        "sub": subject,
        "user_id": user_id,
        "role": role,
        "exp": expires_at
    }

    return jwt.encode(payload, jwt_secret_key, algorithm=jwt_algorithm)