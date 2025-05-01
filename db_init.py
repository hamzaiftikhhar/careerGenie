# db_init.py
# Place this file in the root of your project

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base 
from app.core.config import settings
from app.db.models.user import User
from app.db.models.verification import Verification
from app.db.models.scholarship import Scholarship
from app.db.models.counseling import CounselingSession

import os
print("DB path:", os.path.abspath("app.db"))

def init_db():
    """Initialize the database with all tables."""
    print("Creating database tables...")
    engine = create_engine(settings.DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()