from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id", ondelete="CASCADE"), nullable=False)
    skill_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    preference_score = Column(Float, default=0.0)
    academic_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)  # JSON string of explanation items
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("StudentProfile", back_populates="match_scores")
    internship = relationship("Internship", back_populates="match_scores")
