from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.auth.auth_service import require_role
from app.schemas.schemas import MatchScoreResponse, RecommendationResponse

router = APIRouter(prefix="/api/ai", tags=["AI Matching"])


@router.post("/match/student/{student_id}")
def compute_matches_for_student(
    student_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Compute match scores for a student against all active internships."""
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    from app.services.matching_engine import compute_all_matches_for_student
    matches = compute_all_matches_for_student(db, student)
    return {"message": f"Computed {len(matches)} match scores", "count": len(matches)}


@router.get("/recommendations/{student_id}")
def get_recommendations_for_student(
    student_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Get AI recommendations for a specific student (admin view)."""
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    from app.services.matching_engine import get_student_recommendations
    return get_student_recommendations(db, student)


@router.get("/match/{student_id}/{internship_id}")
def get_match_detail(
    student_id: int,
    internship_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Get detailed match score between a student and internship."""
    from app.services.matching_engine import compute_match_score
    from app.models.internship import Internship

    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    result = compute_match_score(db, student, internship)
    return result
