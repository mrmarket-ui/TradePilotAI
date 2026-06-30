from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.user import UserCreate
from models.user import User
from database.database import get_db
from services.auth_service import hash_password

router = APIRouter()


@router.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        return {"error": "User already exists"}

    # create new user
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