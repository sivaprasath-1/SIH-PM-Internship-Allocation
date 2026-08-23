from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.internship import Internship, InternshipStatus
from app.models.company import Company
from app.models.application import Application, ApplicationStatus
from app.models.student import StudentProfile
from app.models.allocation import Allocation
from app.models.match_score import MatchScore
from app.auth.auth_service import get_current_user, require_role
from app.schemas.schemas import InternshipResponse, ApplicationResponse
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/internships", tags=["Internships"])


def serialize_internship(internship: Internship, db: Session) -> InternshipResponse:
    company = db.query(Company).filter(Company.id == internship.company_id).first()
    app_count = db.query(Application).filter(Application.internship_id == internship.id).count()
    filled = db.query(Allocation).filter(
        Allocation.internship_id == internship.id,
        Allocation.allocation_status.in_(["allocated", "accepted"])
    ).count()

    return InternshipResponse(
        id=internship.id,
        company_id=internship.company_id,
        company_name=company.organization_name if company else None,
        title=internship.title,
        description=internship.description,
        domain=internship.domain,
        location=internship.location,
        work_mode=internship.work_mode.value if hasattr(internship.work_mode, 'value') else str(internship.work_mode),
        duration=internship.duration,
        stipend=internship.stipend,
        seats=internship.seats,
        filled_seats=filled,
        application_deadline=internship.application_deadline,
        minimum_cgpa=internship.minimum_cgpa,
        eligible_degrees=internship.eligible_degrees or [],
        eligible_branches=internship.eligible_branches or [],
        required_skills=internship.required_skills or [],
        preferred_skills=internship.preferred_skills or [],
        status=internship.status.value if hasattr(internship.status, 'value') else str(internship.status),
        application_count=app_count,
        created_at=internship.created_at,
    )


@router.get("", response_model=List[InternshipResponse])
def list_internships(
    domain: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    min_stipend: Optional[float] = None,
    skill: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Internship).filter(Internship.status == InternshipStatus.ACTIVE)

    if domain:
        query = query.filter(Internship.domain.ilike(f"%{domain}%"))
    if location:
        query = query.filter(Internship.location.ilike(f"%{location}%"))
    if work_mode:
        query = query.filter(Internship.work_mode == work_mode)
    if min_stipend:
        query = query.filter(Internship.stipend >= min_stipend)
    if skill:
        query = query.filter(Internship.required_skills.any(skill))
    if search:
        query = query.filter(
            (Internship.title.ilike(f"%{search}%")) |
            (Internship.description.ilike(f"%{search}%")) |
            (Internship.domain.ilike(f"%{search}%"))
        )

    total = query.count()
    internships = query.order_by(Internship.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return [serialize_internship(i, db) for i in internships]


@router.get("/search", response_model=List[InternshipResponse])
def search_internships(
    q: str = Query("", min_length=0),
    domain: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Internship).filter(Internship.status == InternshipStatus.ACTIVE)

    if q:
        query = query.filter(
            (Internship.title.ilike(f"%{q}%")) |
            (Internship.description.ilike(f"%{q}%")) |
            (Internship.domain.ilike(f"%{q}%"))
        )
    if domain:
        query = query.filter(Internship.domain.ilike(f"%{domain}%"))
    if location:
        query = query.filter(Internship.location.ilike(f"%{location}%"))
    if work_mode:
        query = query.filter(Internship.work_mode == work_mode)

    internships = query.order_by(Internship.created_at.desc()).limit(50).all()
    return [serialize_internship(i, db) for i in internships]


@router.get("/{internship_id}", response_model=InternshipResponse)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return serialize_internship(internship, db)


@router.post("/{internship_id}/apply")
def apply_to_internship(
    internship_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    if internship.status != InternshipStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Internship is not accepting applications")

    # Check deadline
    if internship.application_deadline and internship.application_deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Application deadline has passed")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your profile first")

    # Check eligibility
    if internship.minimum_cgpa and profile.cgpa and profile.cgpa < internship.minimum_cgpa:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum CGPA requirement is {internship.minimum_cgpa}. Your CGPA: {profile.cgpa}"
        )

    if internship.eligible_branches and profile.branch:
        if profile.branch not in internship.eligible_branches:
            raise HTTPException(
                status_code=400,
                detail=f"Your branch ({profile.branch}) is not eligible for this internship"
            )

    # Check duplicate
    existing = db.query(Application).filter(
        Application.student_id == profile.id,
        Application.internship_id == internship_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this internship")

    # Check capacity
    filled = db.query(Allocation).filter(
        Allocation.internship_id == internship_id,
        Allocation.allocation_status.in_(["allocated", "accepted"])
    ).count()
    if filled >= internship.seats:
        raise HTTPException(status_code=400, detail="This internship is fully allocated")

    application = Application(
        student_id=profile.id,
        internship_id=internship_id,
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    db.commit()

    # Notify student
    create_notification(
        db, current_user.id,
        title="Application Submitted",
        message=f"Your application for '{internship.title}' has been submitted successfully.",
        notif_type="application"
    )

    # Notify company
    company = db.query(Company).filter(Company.id == internship.company_id).first()
    if company:
        create_notification(
            db, company.user_id,
            title="New Application Received",
            message=f"{current_user.name} has applied for '{internship.title}'.",
            notif_type="application"
        )

    return {"message": "Application submitted successfully", "application_id": application.id}
