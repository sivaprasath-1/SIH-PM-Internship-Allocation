"""
Smart Allocation Engine
Uses constraint optimization to allocate students to internships.
Considers eligibility, capacity, preferences, skills, fairness, and match scores.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import StudentProfile
from app.models.internship import Internship, InternshipStatus
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationRun, AllocationStatus, AllocationRunStatus
from app.models.match_score import MatchScore
from app.models.company import Company
from app.models.skill import Skill, StudentSkill
from app.schemas.schemas import AllocationConfig, AllocationStatistics
from app.services.matching_engine import compute_all_matches_for_student, DEFAULT_WEIGHTS
from app.services.notification_service import create_notification


def run_allocation_engine(
    db: Session,
    config: AllocationConfig,
) -> AllocationRun:
    """
    Run the smart allocation engine.
    Uses a greedy optimization approach with constraint satisfaction.
    Falls back from OR-Tools if not available.
    """
    # Create allocation run record
    run = AllocationRun(
        started_at=datetime.utcnow(),
        status=AllocationRunStatus.RUNNING,
        allocation_config=json.dumps(config.model_dump()),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # Clear previous allocations
        db.query(Allocation).delete()
        db.commit()

        # Get all active internships and their capacities
        internships = db.query(Internship).filter(
            Internship.status == InternshipStatus.ACTIVE
        ).all()

        # Get all students with profiles
        students = db.query(StudentProfile).all()

        if not students or not internships:
            run.status = AllocationRunStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            run.total_students = len(students)
            run.total_internships = len(internships)
            run.total_allocations = 0
            run.unallocated_students = len(students)
            db.commit()
            return run

        # Build weights from config
        weights = {
            "skill": config.skill_weight,
            "semantic": config.semantic_weight,
            "education": config.education_weight,
            "location": config.location_weight,
            "preference": config.preference_weight,
            "academic": config.academic_weight,
        }

        # Ensure all match scores are computed
        for student in students:
            existing_count = db.query(MatchScore).filter(
                MatchScore.student_id == student.id
            ).count()
            if existing_count == 0:
                compute_all_matches_for_student(db, student, weights)

        # Try OR-Tools first, fallback to greedy
        try:
            allocations = _solve_with_ortools(db, students, internships, config)
        except ImportError:
            allocations = _solve_greedy(db, students, internships, config)

        # Create allocation records
        total_allocations = 0
        allocated_student_ids = set()
        first_choice_count = 0

        for student_id, internship_id, score, reason in allocations:
            allocation = Allocation(
                student_id=student_id,
                internship_id=internship_id,
                match_score=score,
                allocation_status=AllocationStatus.ALLOCATED,
                allocated_at=datetime.utcnow(),
                response_deadline=datetime.utcnow() + timedelta(days=7),
                allocation_reason=reason,
            )
            db.add(allocation)
            total_allocations += 1
            allocated_student_ids.add(student_id)

            # Check if this was student's top choice
            top_match = db.query(MatchScore).filter(
                MatchScore.student_id == student_id
            ).order_by(MatchScore.overall_score.desc()).first()
            if top_match and top_match.internship_id == internship_id:
                first_choice_count += 1

            # Notify student
            student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
            if student and student.user:
                internship = db.query(Internship).filter(Internship.id == internship_id).first()
                create_notification(
                    db, student.user_id,
                    title="Internship Allocated!",
                    message=f"You have been allocated to '{internship.title if internship else 'an internship'}'. "
                            f"Match Score: {score}%. Please accept or reject within 7 days.",
                    notif_type="allocation"
                )

        # Update allocation run
        unallocated = len(students) - len(allocated_student_ids)
        avg_score = sum(a[2] for a in allocations) / len(allocations) if allocations else 0
        first_choice_rate = (first_choice_count / len(allocated_student_ids) * 100) if allocated_student_ids else 0

        total_seats = sum(i.seats for i in internships)
        unfilled = total_seats - total_allocations

        run.status = AllocationRunStatus.COMPLETED
        run.completed_at = datetime.utcnow()
        run.total_students = len(students)
        run.total_internships = len(internships)
        run.total_allocations = total_allocations
        run.unallocated_students = unallocated
        run.unfilled_seats = unfilled
        run.avg_match_score = round(avg_score, 1)
        run.first_choice_rate = round(first_choice_rate, 1)

        db.commit()
        return run

    except Exception as e:
        run.status = AllocationRunStatus.FAILED
        run.completed_at = datetime.utcnow()
        db.commit()
        raise e


def _solve_with_ortools(
    db: Session,
    students: List[StudentProfile],
    internships: List[Internship],
    config: AllocationConfig,
) -> List[Tuple[int, int, float, str]]:
    """Solve allocation using Google OR-Tools CP-SAT solver."""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    # Decision variables: x[i][j] = 1 if student i is assigned to internship j
    x = {}
    student_ids = [s.id for s in students]
    internship_ids = [i.id for i in internships]
    internship_seats = {i.id: i.seats for i in internships}

    # Get match scores
    scores = {}
    for student in students:
        for internship in internships:
            match = db.query(MatchScore).filter(
                MatchScore.student_id == student.id,
                MatchScore.internship_id == internship.id,
            ).first()
            score = match.overall_score if match else 0

            # Check eligibility
            eligible = _check_eligibility(student, internship)
            if not eligible:
                score = 0

            scores[(student.id, internship.id)] = int(score * 10)  # Scale for integer solver

    # Create variables
    for s_id in student_ids:
        for i_id in internship_ids:
            x[(s_id, i_id)] = model.NewBoolVar(f"x_{s_id}_{i_id}")

    # Constraint: Each student gets at most one internship
    for s_id in student_ids:
        model.Add(sum(x[(s_id, i_id)] for i_id in internship_ids) <= config.max_allocations_per_student)

    # Constraint: Each internship doesn't exceed capacity
    for i_id in internship_ids:
        model.Add(sum(x[(s_id, i_id)] for s_id in student_ids) <= internship_seats[i_id])

    # Constraint: Only eligible students
    if config.enforce_eligibility:
        for s_id in student_ids:
            for i_id in internship_ids:
                if scores[(s_id, i_id)] == 0:
                    model.Add(x[(s_id, i_id)] == 0)

    # Objective: Maximize total match score
    model.Maximize(
        sum(scores[(s_id, i_id)] * x[(s_id, i_id)]
            for s_id in student_ids
            for i_id in internship_ids)
    )

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    allocations = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for s_id in student_ids:
            for i_id in internship_ids:
                if solver.Value(x[(s_id, i_id)]) == 1:
                    real_score = scores[(s_id, i_id)] / 10.0
                    reason = _generate_allocation_reason(db, s_id, i_id, real_score)
                    allocations.append((s_id, i_id, real_score, reason))

    return allocations


def _solve_greedy(
    db: Session,
    students: List[StudentProfile],
    internships: List[Internship],
    config: AllocationConfig,
) -> List[Tuple[int, int, float, str]]:
    """
    Greedy allocation as fallback.
    Sorts all (student, internship) pairs by score and greedily assigns.
    """
    # Build score matrix
    pairs = []
    for student in students:
        for internship in internships:
            if config.enforce_eligibility and not _check_eligibility(student, internship):
                continue

            match = db.query(MatchScore).filter(
                MatchScore.student_id == student.id,
                MatchScore.internship_id == internship.id,
            ).first()
            score = match.overall_score if match else 0
            if score > 0:
                pairs.append((student.id, internship.id, score))

    # Sort by score descending
    pairs.sort(key=lambda x: x[2], reverse=True)

    # Greedy assignment
    allocated_students = set()
    internship_counts = {i.id: 0 for i in internships}
    internship_seats = {i.id: i.seats for i in internships}
    allocations = []

    for s_id, i_id, score in pairs:
        if s_id in allocated_students:
            continue
        if internship_counts[i_id] >= internship_seats[i_id]:
            continue

        reason = _generate_allocation_reason(db, s_id, i_id, score)
        allocations.append((s_id, i_id, score, reason))
        allocated_students.add(s_id)
        internship_counts[i_id] += 1

    return allocations


def _check_eligibility(student: StudentProfile, internship: Internship) -> bool:
    """Check if a student is eligible for an internship."""
    # CGPA check
    if internship.minimum_cgpa and student.cgpa:
        if student.cgpa < internship.minimum_cgpa:
            return False

    # Branch check
    if internship.eligible_branches:
        if student.branch and student.branch not in internship.eligible_branches:
            return False

    # Degree check
    if internship.eligible_degrees:
        if student.degree and student.degree not in internship.eligible_degrees:
            return False

    return True


def _generate_allocation_reason(db: Session, student_id: int, internship_id: int, score: float) -> str:
    """Generate human-readable allocation reason."""
    match = db.query(MatchScore).filter(
        MatchScore.student_id == student_id,
        MatchScore.internship_id == internship_id,
    ).first()

    if match and match.explanation:
        try:
            exp = json.loads(match.explanation)
            reasons = exp.get("reasons", [])
            return f"Match Score: {score}%. " + "; ".join(reasons[:3])
        except (json.JSONDecodeError, TypeError):
            pass

    return f"Allocated with match score of {score}%"


def compute_allocation_statistics(db: Session) -> AllocationStatistics:
    """Compute comprehensive allocation statistics for the admin dashboard."""
    total_students = db.query(StudentProfile).count()
    total_companies = db.query(Company).count()
    total_internships = db.query(Internship).filter(
        Internship.status == InternshipStatus.ACTIVE
    ).count()
    total_seats = db.query(func.sum(Internship.seats)).filter(
        Internship.status == InternshipStatus.ACTIVE
    ).scalar() or 0

    allocations = db.query(Allocation).filter(
        Allocation.allocation_status.in_(["allocated", "accepted"])
    ).all()

    allocated_student_ids = set(a.student_id for a in allocations)
    allocated_students = len(allocated_student_ids)
    unallocated_students = total_students - allocated_students

    eligible_students = total_students  # Simplified
    allocation_pct = (allocated_students / total_students * 100) if total_students > 0 else 0
    avg_score = sum(a.match_score for a in allocations) / len(allocations) if allocations else 0
    seat_utilization = (allocated_students / total_seats * 100) if total_seats > 0 else 0

    # First choice rate
    first_choice = 0
    for alloc in allocations:
        top_match = db.query(MatchScore).filter(
            MatchScore.student_id == alloc.student_id
        ).order_by(MatchScore.overall_score.desc()).first()
        if top_match and top_match.internship_id == alloc.internship_id:
            first_choice += 1
    first_choice_rate = (first_choice / allocated_students * 100) if allocated_students > 0 else 0

    # By location
    by_location = {}
    for alloc in allocations:
        internship = db.query(Internship).filter(Internship.id == alloc.internship_id).first()
        if internship:
            loc = internship.location or "Unknown"
            by_location[loc] = by_location.get(loc, 0) + 1

    # By branch
    by_branch = {}
    for alloc in allocations:
        student = db.query(StudentProfile).filter(StudentProfile.id == alloc.student_id).first()
        if student:
            branch = student.branch or "Unknown"
            by_branch[branch] = by_branch.get(branch, 0) + 1

    # By domain
    by_domain = {}
    for alloc in allocations:
        internship = db.query(Internship).filter(Internship.id == alloc.internship_id).first()
        if internship:
            domain = internship.domain or "Unknown"
            by_domain[domain] = by_domain.get(domain, 0) + 1

    # By gender (for fairness monitoring)
    by_gender = {}
    for alloc in allocations:
        student = db.query(StudentProfile).filter(StudentProfile.id == alloc.student_id).first()
        if student:
            gender = student.gender or "Not Specified"
            by_gender[gender] = by_gender.get(gender, 0) + 1

    # Skill demand
    skill_demand = {}
    for internship in db.query(Internship).filter(Internship.status == InternshipStatus.ACTIVE).all():
        for skill in (internship.required_skills or []):
            skill_demand[skill] = skill_demand.get(skill, 0) + 1
    skill_demand_list = [{"skill": k, "count": v} for k, v in sorted(skill_demand.items(), key=lambda x: -x[1])[:15]]

    return AllocationStatistics(
        total_students=total_students,
        total_internships=total_internships,
        total_seats=total_seats,
        eligible_students=eligible_students,
        allocated_students=allocated_students,
        unallocated_students=unallocated_students,
        allocation_percentage=round(allocation_pct, 1),
        avg_match_score=round(avg_score, 1),
        first_choice_rate=round(first_choice_rate, 1),
        seat_utilization=round(seat_utilization, 1),
        by_location=by_location,
        by_branch=by_branch,
        by_domain=by_domain,
        by_gender=by_gender,
        skill_demand=skill_demand_list,
    )
