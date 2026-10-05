from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import User, Role
from app.schemas import RegisteredUser, UserRegister, Token
from app.security import hash_password, create_access_token, verify_password
from app.database import get_db

from typing import Annotated



router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


"""--------------------Registers new user endpoint--------------------"""

@router.post(
    "/register",
    response_model=RegisteredUser,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)]
    ) -> RegisteredUser:

    # check wheter user is already registered

    existing_user = db.scalar(select(User).where(User.email == user_data.email))

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
   

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



"""--------------------Login endpoint--------------------"""

@router.post("/login", response_model=Token)
def login( # you MUST write email in OAuth2 "username" in Swagger UI cuz its OAuth2 password flow o_0 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # parses OAuth2 form data instead of JSON to enable the Swagger UI 'Authorize' button
    db: Annotated[Session, Depends(get_db)]
):

    # search user by email
    user = db.scalar(select(User).where(User.email == form_data.username))

    # checking for correct username and password
    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})

    # creating JWT with user data
    access_token = create_access_token(subject=user.email, user_id=user.id, role=user.role.name)

    return Token(access_token=access_token, token_type="bearer")