from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.role import Role
from app.schemas.auth import RegisteredUser, UserRegister
from app.security import hash_password
from app.database import get_db

from typing import Annotated



router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


"""--------------------Registers new user in system--------------------"""

@router.post(
    "/register",
    response_model=RegisteredUser,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Annotated[Sesssion, Depends(get_db)]
    ) -> RegisteredUser:

    # check wheter user is already registered

    existing_user = db.scalar(select(User).where(User.email == user_data.email))

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with cuurrent email already exists")
   

    #  get "Student" role for new user

    student_role = db.scalar(select(Role).where(Role.name == "Student"))

    if not student_role: # quick check
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Student role default is not configured in DB")

    # create new user object

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role_id=student_role.id
    )

    db.add(user) # add to db session

    # trying save user into DB
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError: # in case data error
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email is already exists")

    # return new user data

    return RegisteredUser(
        id=user.id,
        name=user.name,
        email=user.email,
        role=student_role.name
    )

