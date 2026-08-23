from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import json
import os

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.models.application import Application
from app.models.allocation import Allocation
from app.models.match_score import MatchScore
from app.models.internship import Internship
from app.models.company import Company
from app.auth.auth_service import get_current_user, require_role
from app.schemas.schemas import (
    StudentProfileUpdate, StudentProfileResponse, SkillAdd,
    StudentSkillResponse, ApplicationResponse, AllocationResponse,
    RecommendationResponse, MatchScoreResponse, InternshipResponse,
    ResumeAnalysisResponse,
)
from app.services.notification_service import create_notification
from app.config import settings

router = APIRouter(prefix="/api/students", tags=["Students"])


def get_student_profile(user: User, db: Session) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile


def serialize_profile(profile: StudentProfile, db: Session) -> dict:
    user = profile.user
    skills = []
    for ss in profile.skills:
        skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
        skills.append(StudentSkillResponse(
            id=ss.id,
            skill_id=ss.skill_id,
            skill_name=skill.name if skill else "Unknown",
            proficiency_level=ss.proficiency_level,
        ))

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        user_name=user.name if user else None,
        user_email=user.email if user else None,
        date_of_birth=profile.date_of_birth,
        phone=profile.phone,
        gender=profile.gender,
        education_level=profile.education_level,
        degree=profile.degree,
        branch=profile.branch,
        college=profile.college,
        graduation_year=profile.graduation_year,
        cgpa=profile.cgpa,
        location=profile.location,
        preferred_locations=profile.preferred_locations or [],
        preferred_domains=profile.preferred_domains or [],
        bio=profile.bio,
        resume_url=profile.resume_url,
        skills=skills,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("/profile", response_model=StudentProfileResponse)
def get_profile(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    return serialize_profile(profile, db)


@router.put("/profile", response_model=StudentProfileResponse)
def update_profile(
    data: StudentProfileUpdate,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return serialize_profile(profile, db)


@router.post("/skills", response_model=StudentSkillResponse)
def add_skill(
    data: SkillAdd,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)

    # Find or create skill
    skill = db.query(Skill).filter(Skill.name.ilike(data.name.strip())).first()
    if not skill:
        skill = Skill(name=data.name.strip(), category="General")
        db.add(skill)
        db.flush()

    # Check if already added
    existing = db.query(StudentSkill).filter(
        StudentSkill.student_id == profile.id,
        StudentSkill.skill_id == skill.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already added")

    student_skill = StudentSkill(
        student_id=profile.id,
        skill_id=skill.id,
        proficiency_level=data.proficiency_level,
    )
    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)

    return StudentSkillResponse(
        id=student_skill.id,
        skill_id=skill.id,
        skill_name=skill.name,
        proficiency_level=student_skill.proficiency_level,
    )


@router.delete("/skills/{skill_id}")
def remove_skill(
    skill_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    student_skill = db.query(StudentSkill).filter(
        StudentSkill.id == skill_id,
        StudentSkill.student_id == profile.id,
    ).first()
    if not student_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(student_skill)
    db.commit()
    return {"message": "Skill removed"}


@router.post("/resume")
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    contents = file.file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, f"resume_{current_user.id}.pdf")
    with open(filepath, "wb") as f:
        f.write(contents)

    profile = get_student_profile(current_user, db)
    profile.resume_url = filepath
    db.commit()

    # Try to extract skills from resume
    try:
        from app.services.resume_service import extract_resume_data
        analysis = extract_resume_data(filepath)
        return {
            "message": "Resume uploaded successfully",
            "resume_url": filepath,
            "analysis": analysis,
        }
    except Exception:
        return {
            "message": "Resume uploaded successfully",
            "resume_url": filepath,
            "analysis": None,
        }


@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)

    # Ensure match scores exist for this student (compute on the fly if needed)
    match_count = db.query(MatchScore).filter(MatchScore.student_id == profile.id).count()
    if match_count == 0:
        from app.services.matching_engine import compute_all_matches_for_student
        compute_all_matches_for_student(db, profile)

    # Get match scores for this student, ordered by overall score
    matches = db.query(MatchScore).filter(
        MatchScore.student_id == profile.id
    ).order_by(MatchScore.overall_score.desc()).limit(20).all()

    results = []
    for match in matches:
        internship = db.query(Internship).filter(Internship.id == match.internship_id).first()
        if not internship or internship.status != "active":
            continue
        company = db.query(Company).filter(Company.id == internship.company_id).first()

        explanation = []
        skill_gaps = []
        if match.explanation:
            try:
                exp_data = json.loads(match.explanation)
                explanation = exp_data.get("reasons", [])
                skill_gaps = exp_data.get("skill_gaps", [])
            except (json.JSONDecodeError, TypeError):
                explanation = [match.explanation] if match.explanation else []

        filled = db.query(Allocation).filter(
            Allocation.internship_id == internship.id,
            Allocation.allocation_status.in_(["allocated", "accepted"])
        ).count()

        internship_resp = InternshipResponse(
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
            created_at=internship.created_at,
        )

        match_resp = MatchScoreResponse(
            id=match.id,
            student_id=match.student_id,
            internship_id=match.internship_id,
            internship_title=internship.title,
            company_name=company.organization_name if company else None,
            skill_score=match.skill_score,
            education_score=match.education_score,
            location_score=match.location_score,
            preference_score=match.preference_score,
            academic_score=match.academic_score,
            semantic_score=match.semantic_score,
            overall_score=match.overall_score,
            explanation=explanation,
            skill_gaps=skill_gaps,
            created_at=match.created_at,
        )

        results.append(RecommendationResponse(internship=internship_resp, match=match_resp))

    return results


@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    applications = db.query(Application).filter(
        Application.student_id == profile.id
    ).order_by(Application.applied_at.desc()).all()

    results = []
    for app in applications:
        internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
        company = None
        if internship:
            company = db.query(Company).filter(Company.id == internship.company_id).first()

        match = db.query(MatchScore).filter(
            MatchScore.student_id == profile.id,
            MatchScore.internship_id == app.internship_id,
        ).first()

        results.append(ApplicationResponse(
            id=app.id,
            student_id=app.student_id,
            internship_id=app.internship_id,
            student_name=current_user.name,
            internship_title=internship.title if internship else None,
            company_name=company.organization_name if company else None,
            status=app.status.value if hasattr(app.status, 'value') else str(app.status),
            match_score=match.overall_score if match else None,
            applied_at=app.applied_at,
        ))
    return results


@router.get("/allocations", response_model=List[AllocationResponse])
def get_allocations(
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    allocations = db.query(Allocation).filter(
        Allocation.student_id == profile.id
    ).order_by(Allocation.allocated_at.desc()).all()

    results = []
    for alloc in allocations:
        internship = db.query(Internship).filter(Internship.id == alloc.internship_id).first()
        company = None
        if internship:
            company = db.query(Company).filter(Company.id == internship.company_id).first()

        results.append(AllocationResponse(
            id=alloc.id,
            student_id=alloc.student_id,
            internship_id=alloc.internship_id,
            student_name=current_user.name,
            internship_title=internship.title if internship else None,
            company_name=company.organization_name if company else None,
            match_score=alloc.match_score,
            allocation_status=alloc.allocation_status.value if hasattr(alloc.allocation_status, 'value') else str(alloc.allocation_status),
            allocated_at=alloc.allocated_at,
            response_deadline=alloc.response_deadline,
            student_response=alloc.student_response,
            allocation_reason=alloc.allocation_reason,
        ))
    return results


@router.post("/allocations/{allocation_id}/accept")
def accept_allocation(
    allocation_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    allocation = db.query(Allocation).filter(
        Allocation.id == allocation_id,
        Allocation.student_id == profile.id,
    ).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.allocation_status.value != "allocated":
        raise HTTPException(status_code=400, detail="Cannot accept this allocation")

    allocation.allocation_status = "accepted"
    allocation.student_response = "accepted"
    db.commit()

    create_notification(
        db, current_user.id,
        title="Internship Accepted!",
        message="You have accepted your internship allocation.",
        notif_type="success"
    )

    return {"message": "Allocation accepted successfully"}


@router.post("/allocations/{allocation_id}/reject")
def reject_allocation(
    allocation_id: int,
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    db: Session = Depends(get_db),
):
    profile = get_student_profile(current_user, db)
    allocation = db.query(Allocation).filter(
        Allocation.id == allocation_id,
        Allocation.student_id == profile.id,
    ).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    if allocation.allocation_status.value != "allocated":
        raise HTTPException(status_code=400, detail="Cannot reject this allocation")

    allocation.allocation_status = "rejected"
    allocation.student_response = "rejected"
    db.commit()

    create_notification(
        db, current_user.id,
        title="Internship Rejected",
        message="You have rejected your internship allocation.",
        notif_type="warning"
    )

    return {"message": "Allocation rejected"}
