# Import all models here for Alembic autogenerate to work
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.verification import Verification
from app.db.models.scholarship import Scholarship
from app.db.models.counseling import CounselingSession
# from app.db.models.mentorship import MentorshipSession
# from app.db.models.alumni import Alumni
# from app.db.models.feedback import Feedback
# from app.db.models.notification import Notification
# from app.db.models.assessment import Assessment
# from app.db.models.assessment_result import AssessmentResult
# from app.db.models.assessment_question import AssessmentQuestion
# from app.db.models.assessment_option import AssessmentOption
# from app.db.models.assessment_answer import AssessmentAnswer
# from app.db.models.assessment_result_detail import Assessment