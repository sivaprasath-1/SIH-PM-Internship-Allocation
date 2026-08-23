import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


class WorkMode(str, enum.Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class InternshipStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    FILLED = "filled"


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    work_mode = Column(SAEnum(WorkMode), default=WorkMode.ONSITE)
    duration = Column(String(50), nullable=True)  # e.g. "3 months", "6 months"
    stipend = Column(Float, nullable=True)
    seats = Column(Integer, default=1)
    application_deadline = Column(DateTime, nullable=True)
    minimum_cgpa = Column(Float, nullable=True)
    eligible_degrees = Column(ARRAY(String), default=[])
    eligible_branches = Column(ARRAY(String), default=[])
    required_skills = Column(ARRAY(String), default=[])
    preferred_skills = Column(ARRAY(String), default=[])
    status = Column(SAEnum(InternshipStatus), default=InternshipStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="internships")
    applications = relationship("Application", back_populates="internship", cascade="all, delete-orphan")
    match_scores = relationship("MatchScore", back_populates="internship", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="internship", cascade="all, delete-orphan")
