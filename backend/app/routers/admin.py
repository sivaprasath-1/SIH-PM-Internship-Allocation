from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.company import Company, VerificationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.application import Application
from app.models.allocation import Allocation, AllocationRun
from app.models.match_score import MatchScore
from app.models.skill import Skill, StudentSkill
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.auth.auth_service import require_role
from app.schemas.schemas import (
    DashboardStats, ApplicationResponse, AllocationResponse,
    AllocationRunResponse, AllocationStatistics, AllocationConfig,
    AuditLogResponse, StudentProfileResponse, CompanyResponse,
    InternshipResponse,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    total_students = db.query(StudentProfile).count()
    total_companies = db.query(Company).count()
    total_internships = db.query(Internship).count()
    total_seats = db.query(func.sum(Internship.seats)).scalar() or 0
    total_applications = db.query(Application).count()
    allocated_students = db.query(Allocation).filter(
        Allocation.allocation_status.in_(["allocated", "accepted"])
    ).distinct(Allocation.student_id).count()
    verified_companies = db.query(Company).filter(
        Company.verification_status == VerificationStatus.VERIFIED
    ).count()
    active_internships = db.query(Internship).filter(
        Internship.status == InternshipStatus.ACTIVE
    ).count()

    unallocated_students = total_students - allocated_students
    allocation_pct = (allocated_students / total_students * 100) if total_students > 0 else 0

    avg_score = db.query(func.avg(Allocation.match_score)).scalar() or 0.0

    # Students by branch
    branch_counts = db.query(
        StudentProfile.branch, func.count(StudentProfile.id)
    ).group_by(StudentProfile.branch).all()
    students_by_branch = {b or "Unknown": c for b, c in branch_counts}

    # Internships by domain
    domain_counts = db.query(
        Internship.domain, func.count(Internship.id)
    ).group_by(Internship.domain).all()
    internships_by_domain = {d or "Unknown": c for d, c in domain_counts}

    # Recent applications
    recent_apps = db.query(Application).order_by(
        Application.applied_at.desc()
    ).limit(10).all()

    recent_app_responses = []
    for app in recent_apps:
        student = db.query(StudentProfile).filter(StudentProfile.id == app.student_id).first()
        internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
        company = db.query(Company).filter(Company.id == internship.company_id).first() if internship else None
        user = student.user if student else None

        recent_app_responses.append(ApplicationResponse(
            id=app.id,
            student_id=app.student_id,
            internship_id=app.internship_id,
            student_name=user.name if user else None,
            internship_title=internship.title if internship else None,
            company_name=company.organization_name if company else None,
            status=app.status.value if hasattr(app.status, 'value') else str(app.status),
            applied_at=app.applied_at,
        ))

    return DashboardStats(
        total_students=total_students,
        total_companies=total_companies,
        total_internships=total_internships,
        total_seats=total_seats,
        total_applications=total_applications,
        allocated_students=allocated_students,
        unallocated_students=unallocated_students,
        allocation_percentage=round(allocation_pct, 1),
        avg_match_score=round(avg_score, 1),
        verified_companies=verified_companies,
        active_internships=active_internships,
        students_by_branch=students_by_branch,
        internships_by_domain=internships_by_domain,
        recent_applications=recent_app_responses,
    )


@router.get("/students")
def list_students(
    branch: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    query = db.query(StudentProfile)
    if branch:
        query = query.filter(StudentProfile.branch.ilike(f"%{branch}%"))
    if location:
        query = query.filter(StudentProfile.location.ilike(f"%{location}%"))
    if search:
        query = query.join(User).filter(
            (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    total = query.count()
    students = query.offset((page - 1) * limit).limit(limit).all()

    results = []
    for s in students:
        user = s.user
        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "branch": s.branch,
            "degree": s.degree,
            "college": s.college,
            "cgpa": s.cgpa,
            "location": s.location,
            "graduation_year": s.graduation_year,
            "is_active": user.is_active if user else False,
        })

    return {"total": total, "students": results}


@router.get("/companies")
def list_companies(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    query = db.query(Company)
    if status:
        query = query.filter(Company.verification_status == status)
    if search:
        query = query.filter(Company.organization_name.ilike(f"%{search}%"))

    total = query.count()
    companies = query.offset((page - 1) * limit).limit(limit).all()

    results = []
    for c in companies:
        internship_count = db.query(Internship).filter(Internship.company_id == c.id).count()
        results.append({
            "id": c.id,
            "user_id": c.user_id,
            "organization_name": c.organization_name,
            "industry": c.industry,
            "location": c.location,
            "verification_status": c.verification_status.value if hasattr(c.verification_status, 'value') else str(c.verification_status),
            "internship_count": internship_count,
            "created_at": str(c.created_at) if c.created_at else None,
        })

    return {"total": total, "companies": results}


@router.post("/companies/{company_id}/verify")
def verify_company(
    company_id: int,
    action: str = Query(..., pattern="^(verified|rejected)$"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.verification_status = VerificationStatus(action)
    db.commit()

    from app.services.notification_service import create_notification
    create_notification(
        db, company.user_id,
        title=f"Organization {action.title()}",
        message=f"Your organization has been {action} by the admin.",
        notif_type="info"
    )

    return {"message": f"Company {action}"}


@router.get("/internships")
def list_all_internships(
    domain: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    query = db.query(Internship)
    if domain:
        query = query.filter(Internship.domain.ilike(f"%{domain}%"))
    if status_filter:
        query = query.filter(Internship.status == status_filter)
    if search:
        query = query.filter(Internship.title.ilike(f"%{search}%"))

    total = query.count()
    internships = query.order_by(Internship.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    results = []
    for i in internships:
        company = db.query(Company).filter(Company.id == i.company_id).first()
        app_count = db.query(Application).filter(Application.internship_id == i.id).count()
        filled = db.query(Allocation).filter(
            Allocation.internship_id == i.id,
            Allocation.allocation_status.in_(["allocated", "accepted"])
        ).count()
        results.append({
            "id": i.id,
            "title": i.title,
            "company_name": company.organization_name if company else None,
            "domain": i.domain,
            "location": i.location,
            "seats": i.seats,
            "filled_seats": filled,
            "application_count": app_count,
            "status": i.status.value if hasattr(i.status, 'value') else str(i.status),
            "stipend": i.stipend,
            "created_at": str(i.created_at) if i.created_at else None,
        })

    return {"total": total, "internships": results}


@router.get("/applications")
def list_all_applications(
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    query = db.query(Application)
    if status_filter:
        query = query.filter(Application.status == status_filter)

    total = query.count()
    applications = query.order_by(Application.applied_at.desc()).offset((page - 1) * limit).limit(limit).all()

    results = []
    for app in applications:
        student = db.query(StudentProfile).filter(StudentProfile.id == app.student_id).first()
        internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
        company = db.query(Company).filter(Company.id == internship.company_id).first() if internship else None
        user = student.user if student else None

        results.append({
            "id": app.id,
            "student_id": app.student_id,
            "student_name": user.name if user else None,
            "internship_id": app.internship_id,
            "internship_title": internship.title if internship else None,
            "company_name": company.organization_name if company else None,
            "status": app.status.value if hasattr(app.status, 'value') else str(app.status),
            "applied_at": str(app.applied_at) if app.applied_at else None,
        })

    return {"total": total, "applications": results}


@router.post("/allocation/run", response_model=AllocationRunResponse)
def run_allocation(
    config: AllocationConfig = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Run the AI allocation engine."""
    if config is None:
        config = AllocationConfig()

    from app.services.allocation_engine import run_allocation_engine
    result = run_allocation_engine(db, config)

    # Create audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="RUN_ALLOCATION",
        entity_type="allocation_run",
        entity_id=result.id,
        metadata_json=json.dumps(config.model_dump()),
    )
    db.add(audit)
    db.commit()

    return AllocationRunResponse.model_validate(result)


@router.get("/allocation/results", response_model=List[AllocationResponse])
def get_allocation_results(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    allocations = db.query(Allocation).order_by(Allocation.match_score.desc()).all()
    results = []
    for alloc in allocations:
        student = db.query(StudentProfile).filter(StudentProfile.id == alloc.student_id).first()
        internship = db.query(Internship).filter(Internship.id == alloc.internship_id).first()
        company = db.query(Company).filter(Company.id == internship.company_id).first() if internship else None
        user = student.user if student else None

        results.append(AllocationResponse(
            id=alloc.id,
            student_id=alloc.student_id,
            internship_id=alloc.internship_id,
            student_name=user.name if user else None,
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


@router.get("/allocation/statistics", response_model=AllocationStatistics)
def get_allocation_statistics(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    from app.services.allocation_engine import compute_allocation_statistics
    return compute_allocation_statistics(db)


@router.get("/allocation/unallocated-students")
def get_unallocated_students(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    allocated_ids = [a.student_id for a in db.query(Allocation).filter(
        Allocation.allocation_status.in_(["allocated", "accepted"])
    ).all()]

    students = db.query(StudentProfile).filter(
        ~StudentProfile.id.in_(allocated_ids) if allocated_ids else True
    ).all()

    return [{
        "id": s.id,
        "name": s.user.name if s.user else None,
        "branch": s.branch,
        "college": s.college,
        "cgpa": s.cgpa,
        "location": s.location,
    } for s in students]


@router.get("/allocation/unfilled-internships")
def get_unfilled_internships(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    internships = db.query(Internship).filter(Internship.status == InternshipStatus.ACTIVE).all()
    results = []
    for i in internships:
        filled = db.query(Allocation).filter(
            Allocation.internship_id == i.id,
            Allocation.allocation_status.in_(["allocated", "accepted"])
        ).count()
        if filled < i.seats:
            company = db.query(Company).filter(Company.id == i.company_id).first()
            results.append({
                "id": i.id,
                "title": i.title,
                "company_name": company.organization_name if company else None,
                "seats": i.seats,
                "filled": filled,
                "remaining": i.seats - filled,
                "domain": i.domain,
                "location": i.location,
            })
    return results


@router.get("/audit-logs")
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    total = db.query(AuditLog).count()
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    results = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        results.append({
            "id": log.id,
            "user_id": log.user_id,
            "user_name": user.name if user else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "metadata_json": log.metadata_json,
            "created_at": str(log.created_at) if log.created_at else None,
        })

    return {"total": total, "logs": results}
