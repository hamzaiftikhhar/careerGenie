# Import all the models, so that Base has them before being imported by Alembic
from app.db.session import Base

# Import all models here
from app.db.models.user import User
from app.db.models.verification import Verification
from app.db.models.scholarship import Scholarship
from app.db.models.counseling import CounselingSession