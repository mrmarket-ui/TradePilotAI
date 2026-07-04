from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from schemas.user import UserCreate
from schemas.login import LoginRequest

from services.auth_service import (
    hash_password,
    verify_password
)

from services.jwt_service import create_access_token
from services.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from services.dependencies import get_current_user
router = APIRouter()


@router.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {"error": "User already exists"}

    # Create new user
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": existing_user.email,
            "id": existing_user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }