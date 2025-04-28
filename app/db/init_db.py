import logging
import sys
from pathlib import Path

# Add parent directory to sys.path to allow importing app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.db.base import Base
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    """Initialize the database."""
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Created database tables")
        
        # Initialize data
        init_db(db)
        logger.info("Database initialized successfully")
    finally:
        db.close()


def main() -> None:
    logger.info("Initializing database")
    init()
    logger.info("Database initialization completed")


if __name__ == "__main__":
    main()