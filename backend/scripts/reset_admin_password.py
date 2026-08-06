import getpass

import main

from database.database import SessionLocal
from models.user import User
from services.auth_service import hash_password


email = input("Admin email: ").strip().lower()
password = getpass.getpass("New password: ")
confirm = getpass.getpass("Confirm password: ")

if password != confirm:
    raise RuntimeError("Passwords do not match.")

if len(password) < 8:
    raise RuntimeError("Password must contain at least 8 characters.")

db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise RuntimeError("User not found.")

    user.password_hash = hash_password(password)
    user.plan = "premium"
    user.is_admin = True
    user.is_active = True
    user.ai_credits = 100000

    db.commit()
    db.refresh(user)

    print("")
    print("PASSWORD UPDATED")
    print("ID:", user.id)
    print("EMAIL:", user.email)
    print("ADMIN:", user.is_admin)
    print("PLAN:", user.plan)
    print("ACTIVE:", user.is_active)

finally:
    db.close()
