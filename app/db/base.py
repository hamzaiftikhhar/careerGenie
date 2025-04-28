# Import all models here for Alembic autogenerate to work
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.verification import Verification
from app.db.models.scholarship import Scholarship
from app.db.models.counseling import CounselingSession