import os
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import SessionLocal
from app.models import User, Role
from app.security import hash_password

load_dotenv()

DEMO = [
    ("Demo Teacher", "teacher@deskin.test", "Teacher"),
    ("Demo Admin", "admin@deskin.test", "Admin"),
]


def main():
    password = os.environ["DEMO_PASSWORD"]
    with SessionLocal() as db:
        for name, email, role_name in DEMO:
            if db.scalar(select(User).where(User.email == email)):
                print(f"skip {email}")
                continue
            role = db.scalar(select(Role).where(Role.name == role_name))
            db.add(User(name=name, email=email,
                        password_hash=hash_password(password), role_id=role.id))
            print(f"created {email} ({role_name})")
        db.commit()


if __name__ == "__main__":
    main()
