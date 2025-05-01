# fyp/scripts/init_db.py
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.exc import ProgrammingError

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.schemas.user import UserCreate
from app.crud.user import user as user_crud

# Create tables
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create initial superuser if it doesn't exist
        if not user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL):
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                first_name="Admin",
                last_name="User",
                is_superuser=True,
                is_verified=True
            )
            user_crud.create(db, obj_in=user_in)
            print(f"Superuser {settings.FIRST_SUPERUSER_EMAIL} created.")
        else:
            print(f"Superuser {settings.FIRST_SUPERUSER_EMAIL} already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database initialization completed!")