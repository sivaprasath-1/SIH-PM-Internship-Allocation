from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.internship import Internship, InternshipStatus, WorkMode
from app.models.application import Application
from app.models.allocation import Allocation
from app.models.match_score import MatchScore
from app.models.student import StudentProfile
from app.auth.auth_service import require_role
from app.schemas.schemas import (
    CompanyProfileUpdate, CompanyResponse, InternshipCreate, InternshipUpdate,
    InternshipResponse, ApplicationResponse, MatchScoreResponse,
)
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/companies", tags=["Companies"])


def get_company(user: User, db: Session) -> Company:
    company = db.query(Company).filter(Company.user_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return company


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


@router.get("/profile", response_model=CompanyResponse)
def get_profile(
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    return CompanyResponse.model_validate(company)


@router.put("/profile", response_model=CompanyResponse)
def update_profile(
    data: CompanyProfileUpdate,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return CompanyResponse.model_validate(company)


@router.post("/internships", response_model=InternshipResponse)
def create_internship(
    data: InternshipCreate,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internship = Internship(
        company_id=company.id,
        title=data.title,
        description=data.description,
        domain=data.domain,
        location=data.location,
        work_mode=WorkMode(data.work_mode),
        duration=data.duration,
        stipend=data.stipend,
        seats=data.seats,
        application_deadline=data.application_deadline,
        minimum_cgpa=data.minimum_cgpa,
        eligible_degrees=data.eligible_degrees or [],
        eligible_branches=data.eligible_branches or [],
        required_skills=data.required_skills or [],
        preferred_skills=data.preferred_skills or [],
        status=InternshipStatus.ACTIVE,
    )
    db.add(internship)
    db.commit()
    db.refresh(internship)
    return serialize_internship(internship, db)


@router.get("/internships", response_model=List[InternshipResponse])
def list_internships(
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internships = db.query(Internship).filter(
        Internship.company_id == company.id
    ).order_by(Internship.created_at.desc()).all()
    return [serialize_internship(i, db) for i in internships]


@router.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship(
    internship_id: int,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internship = db.query(Internship).filter(
        Internship.id == internship_id,
        Internship.company_id == company.id,
    ).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return serialize_internship(internship, db)


@router.put("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(
    internship_id: int,
    data: InternshipUpdate,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internship = db.query(Internship).filter(
        Internship.id == internship_id,
        Internship.company_id == company.id,
    ).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "work_mode" and value:
            value = WorkMode(value)
        if key == "status" and value:
            value = InternshipStatus(value)
        setattr(internship, key, value)

    db.commit()
    db.refresh(internship)
    return serialize_internship(internship, db)


@router.delete("/internships/{internship_id}")
def delete_internship(
    internship_id: int,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internship = db.query(Internship).filter(
        Internship.id == internship_id,
        Internship.company_id == company.id,
    ).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    db.delete(internship)
    db.commit()
    return {"message": "Internship deleted"}


@router.get("/internships/{internship_id}/applications", response_model=List[ApplicationResponse])
def get_internship_applications(
    internship_id: int,
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    company = get_company(current_user, db)
    internship = db.query(Internship).filter(
        Internship.id == internship_id,
        Internship.company_id == company.id,
    ).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    applications = db.query(Application).filter(
        Application.internship_id == internship_id
    ).order_by(Application.applied_at.desc()).all()

    results = []
    for app in applications:
        student = db.query(StudentProfile).filter(StudentProfile.id == app.student_id).first()
        user = student.user if student else None
        match = db.query(MatchScore).filter(
            MatchScore.student_id == app.student_id,
            MatchScore.internship_id == internship_id,
        ).first()

        results.append(ApplicationResponse(
            id=app.id,
            student_id=app.student_id,
            internship_id=app.internship_id,
            student_name=user.name if user else None,
            internship_title=internship.title,
            company_name=company.organization_name,
            status=app.status.value if hasattr(app.status, 'value') else str(app.status),
            match_score=match.overall_score if match else None,
            applied_at=app.applied_at,
        ))
    return results


@router.get("/candidates", response_model=List[dict])
def get_recommended_candidates(
    current_user: User = Depends(require_role(UserRole.COMPANY)),
    db: Session = Depends(get_db),
):
    """Get top candidates across all company internships based on match scores."""
    company = get_company(current_user, db)
    internships = db.query(Internship).filter(
        Internship.company_id == company.id,
        Internship.status == InternshipStatus.ACTIVE,
    ).all()

    candidates = []
    for internship in internships:
        matches = db.query(MatchScore).filter(
            MatchScore.internship_id == internship.id,
        ).order_by(MatchScore.overall_score.desc()).limit(10).all()

        for match in matches:
            student = db.query(StudentProfile).filter(StudentProfile.id == match.student_id).first()
            if not student:
                continue
            user = student.user
            candidates.append({
                "student_id": student.id,
                "student_name": user.name if user else None,
                "branch": student.branch,
                "cgpa": student.cgpa,
                "college": student.college,
                "internship_id": internship.id,
                "internship_title": internship.title,
                "match_score": match.overall_score,
            })

    # Sort by match score and deduplicate
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:50]
