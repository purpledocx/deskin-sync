from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status

from typing import Annotated

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.security import jwt_secret_key, jwt_algorithm

from jose import jwt, JWTError



# scheme of getting token from "Authorization" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



#exeption returned if token validation error 
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
    )



def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
    ) -> User:
    """ gets user based on JWT token """

    # try to decode JWT
    try:
        payload = jwt.decode(token, jwt_secret_key, [jwt_algorithm]) #added attr cuz its a list
        # get email from "subject"
        email = payload.get("sub")


    except JWTError:
        raise credentials_exception

    #search user in DB by email
    user = db.scalar(select(User).where(User.email == email))

    if not user:
        raise credentials_exception


    return user