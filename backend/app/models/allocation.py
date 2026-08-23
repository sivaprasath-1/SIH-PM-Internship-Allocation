import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class AllocationStatus(str, enum.Enum):
    ALLOCATED = "allocated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REALLOCATED = "reallocated"


class AllocationRunStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, default=0.0)
    allocation_status = Column(SAEnum(AllocationStatus), default=AllocationStatus.ALLOCATED)
    allocated_at = Column(DateTime, default=datetime.utcnow)
    response_deadline = Column(DateTime, nullable=True)
    student_response = Column(String(20), nullable=True)
    allocation_reason = Column(Text, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="allocations")
    internship = relationship("Internship", back_populates="allocations")


class AllocationRun(Base):
    __tablename__ = "allocation_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(SAEnum(AllocationRunStatus), default=AllocationRunStatus.RUNNING)
    total_students = Column(Integer, default=0)
    total_internships = Column(Integer, default=0)
    total_allocations = Column(Integer, default=0)
    unallocated_students = Column(Integer, default=0)
    unfilled_seats = Column(Integer, default=0)
    avg_match_score = Column(Float, default=0.0)
    first_choice_rate = Column(Float, default=0.0)
    allocation_config = Column(Text, nullable=True)  # JSON string of config
