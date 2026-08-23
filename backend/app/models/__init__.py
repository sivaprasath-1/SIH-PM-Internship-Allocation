# Models package
from app.models.user import User
from app.models.student import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.models.company import Company
from app.models.internship import Internship
from app.models.application import Application
from app.models.match_score import MatchScore
from app.models.allocation import Allocation, AllocationRun
from app.models.notification import Notification
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "StudentProfile",
    "Skill",
    "StudentSkill",
    "Company",
    "Internship",
    "Application",
    "MatchScore",
    "Allocation",
    "AllocationRun",
    "Notification",
    "AuditLog",
]
