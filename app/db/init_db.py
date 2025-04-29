import logging
from sqlalchemy.orm import Session

from app.crud.user import user
from app.schemas.user import UserCreate
from app.core.config import settings


def init_db(db: Session) -> None:
    """Initialize the database with a first superuser."""
    # Check if we need to create a first superuser
    if settings.FIRST_SUPERUSER_EMAIL and settings.FIRST_SUPERUSER_PASSWORD:
        superuser = user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not superuser:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_verified=True
            )
            superuser = user.create(db, obj_in=user_in)
            logging.info(f"Created first superuser: {superuser.email}")
        else:
            logging.info("First superuser already exists in database")