"""
AI Matching Engine
Computes multi-factor match scores between students and internships.
Uses TF-IDF for semantic similarity, plus rule-based scoring for
skills, education, location, preferences, and academics.
"""
import json
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import numpy as np

from app.models.student import StudentProfile
from app.models.internship import Internship, InternshipStatus
from app.models.skill import Skill, StudentSkill
from app.models.match_score import MatchScore
from app.models.company import Company

# Default weights (configurable by admin)
DEFAULT_WEIGHTS = {
    "skill": 0.35,
    "semantic": 0.20,
    "education": 0.15,
    "location": 0.10,
    "preference": 0.10,
    "academic": 0.10,
}


def compute_match_score(
    db: Session,
    student: StudentProfile,
    internship: Internship,
    weights: Dict[str, float] = None,
) -> Dict:
    """
    Compute a detailed match score between a student and internship.
    Returns a dictionary with all sub-scores and explanations.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Get student skills
    student_skills = _get_student_skills(db, student)

    # Compute individual scores
    skill_result = _compute_skill_score(student_skills, internship)
    education_result = _compute_education_score(student, internship)
    location_result = _compute_location_score(student, internship)
    preference_result = _compute_preference_score(student, internship)
    academic_result = _compute_academic_score(student, internship)
    semantic_result = _compute_semantic_score(student, internship, student_skills)

    # Calculate weighted overall score
    overall = (
        skill_result["score"] * weights["skill"]
        + semantic_result["score"] * weights["semantic"]
        + education_result["score"] * weights["education"]
        + location_result["score"] * weights["location"]
        + preference_result["score"] * weights["preference"]
        + academic_result["score"] * weights["academic"]
    )
    overall = min(100, max(0, round(overall, 1)))

    # Collect explanations
    reasons = []
    skill_gaps = []

    reasons.extend(skill_result.get("reasons", []))
    reasons.extend(education_result.get("reasons", []))
    reasons.extend(location_result.get("reasons", []))
    reasons.extend(preference_result.get("reasons", []))
    reasons.extend(academic_result.get("reasons", []))
    reasons.extend(semantic_result.get("reasons", []))
    skill_gaps = skill_result.get("gaps", [])

    explanation_data = {
        "reasons": reasons,
        "skill_gaps": skill_gaps,
    }

    return {
        "student_id": int(student.id),
        "internship_id": int(internship.id),
        "skill_score": float(round(skill_result["score"], 1)),
        "education_score": float(round(education_result["score"], 1)),
        "location_score": float(round(location_result["score"], 1)),
        "preference_score": float(round(preference_result["score"], 1)),
        "academic_score": float(round(academic_result["score"], 1)),
        "semantic_score": float(round(semantic_result["score"], 1)),
        "overall_score": float(overall),
        "explanation": explanation_data,
    }


def _get_student_skills(db: Session, student: StudentProfile) -> List[str]:
    """Get list of skill names for a student."""
    student_skills = db.query(StudentSkill).filter(
        StudentSkill.student_id == student.id
    ).all()
    skills = []
    for ss in student_skills:
        skill = db.query(Skill).filter(Skill.id == ss.skill_id).first()
        if skill:
            skills.append(skill.name)
    return skills


def _compute_skill_score(student_skills: List[str], internship: Internship) -> Dict:
    """Compute skill compatibility score."""
    required = internship.required_skills or []
    preferred = internship.preferred_skills or []

    if not required and not preferred:
        return {"score": 70, "reasons": ["No specific skills required"], "gaps": []}

    student_skills_lower = [s.lower() for s in student_skills]
    reasons = []
    gaps = []

    # Required skills matching
    required_matched = 0
    for skill in required:
        if skill.lower() in student_skills_lower:
            required_matched += 1
        else:
            gaps.append(skill)

    # Preferred skills matching
    preferred_matched = 0
    for skill in preferred:
        if skill.lower() in student_skills_lower:
            preferred_matched += 1

    # Score calculation
    if required:
        required_ratio = required_matched / len(required)
        required_score = required_ratio * 80  # Up to 80 points from required skills
    else:
        required_score = 60
        required_ratio = 1.0

    if preferred:
        preferred_ratio = preferred_matched / len(preferred)
        preferred_score = preferred_ratio * 20  # Up to 20 points from preferred skills
    else:
        preferred_score = 10
        preferred_ratio = 1.0

    score = required_score + preferred_score

    # Generate explanations
    if required:
        reasons.append(f"{required_matched} of {len(required)} required skills match")
    if preferred and preferred_matched > 0:
        reasons.append(f"{preferred_matched} of {len(preferred)} preferred skills match")
    if gaps:
        reasons.append(f"Missing skills: {', '.join(gaps[:3])}")

    return {"score": min(100, score), "reasons": reasons, "gaps": gaps}


def _compute_education_score(student: StudentProfile, internship: Internship) -> Dict:
    """Compute education compatibility score."""
    reasons = []
    score = 50  # Base score

    eligible_degrees = internship.eligible_degrees or []
    eligible_branches = internship.eligible_branches or []

    # Degree matching
    if eligible_degrees:
        if student.degree and student.degree in eligible_degrees:
            score += 25
            reasons.append(f"Your {student.degree} degree satisfies the eligibility requirement")
        elif not student.degree:
            score += 10  # Unknown, give partial
        else:
            score -= 20
            reasons.append(f"Your degree ({student.degree}) may not match the requirement")
    else:
        score += 25
        reasons.append("No specific degree requirement")

    # Branch matching
    if eligible_branches:
        if student.branch and student.branch in eligible_branches:
            score += 25
            reasons.append(f"Your {student.branch} branch is eligible")
        elif not student.branch:
            score += 10
        else:
            score -= 20
            reasons.append(f"Your branch ({student.branch}) may not be eligible")
    else:
        score += 25
        reasons.append("No specific branch requirement")

    return {"score": max(0, min(100, score)), "reasons": reasons}


def _compute_location_score(student: StudentProfile, internship: Internship) -> Dict:
    """Compute location compatibility score."""
    reasons = []
    score = 50

    intern_location = (internship.location or "").lower().strip()
    student_location = (student.location or "").lower().strip()
    preferred_locations = [l.lower().strip() for l in (student.preferred_locations or [])]

    if not intern_location:
        return {"score": 70, "reasons": ["Remote/flexible location"]}

    # Check work mode
    work_mode = internship.work_mode
    if hasattr(work_mode, 'value'):
        work_mode = work_mode.value
    if work_mode == "remote":
        return {"score": 90, "reasons": ["Remote internship - location flexible"]}

    # Exact match with student location
    if student_location and intern_location == student_location:
        score = 100
        reasons.append("Internship location matches your current location")
    elif intern_location in preferred_locations:
        score = 95
        reasons.append("Internship location matches your preferred location")
    elif student_location and _locations_in_same_state(intern_location, student_location):
        score = 75
        reasons.append("Internship is in the same state as your location")
    elif preferred_locations:
        # Check if any preferred location is in the same state
        for pref in preferred_locations:
            if _locations_in_same_state(intern_location, pref):
                score = 70
                reasons.append("Internship is near one of your preferred locations")
                break
    else:
        score = 40
        reasons.append(f"Internship is in {internship.location}")

    return {"score": max(0, min(100, score)), "reasons": reasons}


def _locations_in_same_state(loc1: str, loc2: str) -> bool:
    """Check if two Indian locations are in the same state (simplified)."""
    state_cities = {
        "maharashtra": ["mumbai", "pune", "nagpur", "nashik"],
        "karnataka": ["bangalore", "bengaluru", "mysore", "hubli"],
        "tamil nadu": ["chennai", "coimbatore", "madurai", "salem"],
        "telangana": ["hyderabad", "warangal", "nizamabad"],
        "delhi": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
        "uttar pradesh": ["lucknow", "noida", "kanpur", "agra", "varanasi"],
        "west bengal": ["kolkata", "howrah", "durgapur"],
        "gujarat": ["ahmedabad", "surat", "vadodara", "rajkot"],
        "rajasthan": ["jaipur", "jodhpur", "udaipur", "kota"],
        "kerala": ["kochi", "cochin", "thiruvananthapuram", "kozhikode"],
    }

    for state, cities in state_cities.items():
        if loc1 in cities and loc2 in cities:
            return True
    return False


def _compute_preference_score(student: StudentProfile, internship: Internship) -> Dict:
    """Compute preference alignment score."""
    reasons = []
    score = 50

    preferred_domains = [d.lower().strip() for d in (student.preferred_domains or [])]
    intern_domain = (internship.domain or "").lower().strip()

    if not preferred_domains:
        return {"score": 60, "reasons": ["No preferred domains specified"]}

    if intern_domain in preferred_domains:
        score = 100
        reasons.append(f"Your preferred domain ({internship.domain}) matches this internship")
    else:
        # Partial matching
        for pref in preferred_domains:
            if pref in intern_domain or intern_domain in pref:
                score = 80
                reasons.append(f"Domain partially matches your preference ({pref})")
                break
        else:
            score = 30
            reasons.append(f"Domain ({internship.domain}) doesn't match your preferences")

    return {"score": max(0, min(100, score)), "reasons": reasons}


def _compute_academic_score(student: StudentProfile, internship: Internship) -> Dict:
    """Compute academic performance score."""
    reasons = []

    if not student.cgpa:
        return {"score": 50, "reasons": ["Academic performance not specified"]}

    min_cgpa = internship.minimum_cgpa or 0

    if student.cgpa >= min_cgpa:
        # Scale score based on CGPA
        if student.cgpa >= 9.0:
            score = 100
            reasons.append(f"Excellent CGPA ({student.cgpa})")
        elif student.cgpa >= 8.0:
            score = 90
            reasons.append(f"Very good CGPA ({student.cgpa})")
        elif student.cgpa >= 7.0:
            score = 75
            reasons.append(f"Good CGPA ({student.cgpa})")
        elif student.cgpa >= 6.0:
            score = 60
            reasons.append(f"CGPA ({student.cgpa}) meets requirement")
        else:
            score = 50
            reasons.append(f"CGPA ({student.cgpa}) meets minimum requirement")

        if min_cgpa > 0:
            reasons.append(f"Your CGPA satisfies the minimum requirement of {min_cgpa}")
    else:
        score = 20
        reasons.append(f"Your CGPA ({student.cgpa}) is below the minimum ({min_cgpa})")

    return {"score": max(0, min(100, score)), "reasons": reasons}


def _compute_semantic_score(
    student: StudentProfile, internship: Internship, student_skills: List[str]
) -> Dict:
    """
    Compute semantic similarity between student profile and internship.
    Uses TF-IDF cosine similarity as a lightweight approach.
    """
    reasons = []

    # Build student text profile
    student_text_parts = []
    if student.bio:
        student_text_parts.append(student.bio)
    if student.branch:
        student_text_parts.append(student.branch)
    if student.degree:
        student_text_parts.append(student.degree)
    student_text_parts.extend(student_skills)
    if student.preferred_domains:
        student_text_parts.extend(student.preferred_domains)

    student_text = " ".join(student_text_parts)

    # Build internship text profile
    intern_text_parts = []
    if internship.title:
        intern_text_parts.append(internship.title)
    if internship.description:
        intern_text_parts.append(internship.description)
    if internship.domain:
        intern_text_parts.append(internship.domain)
    if internship.required_skills:
        intern_text_parts.extend(internship.required_skills)
    if internship.preferred_skills:
        intern_text_parts.extend(internship.preferred_skills)

    intern_text = " ".join(intern_text_parts)

    if not student_text or not intern_text:
        return {"score": 50, "reasons": ["Insufficient data for semantic analysis"]}

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([student_text, intern_text])
        similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])

        score = float(similarity * 100)

        if score >= 70:
            reasons.append("Strong semantic match between your profile and internship")
        elif score >= 40:
            reasons.append("Moderate semantic similarity with internship requirements")
        else:
            reasons.append("Low semantic similarity — internship may be outside your core area")

    except ImportError:
        # Fallback: simple keyword overlap
        student_words = set(student_text.lower().split())
        intern_words = set(intern_text.lower().split())
        overlap = len(student_words & intern_words)
        total = max(len(student_words | intern_words), 1)
        score = float((overlap / total) * 100)
        reasons.append("Basic keyword matching used (sklearn not available)")

    return {"score": float(max(0.0, min(100.0, round(score, 1)))), "reasons": reasons}


def compute_all_matches_for_student(
    db: Session,
    student: StudentProfile,
    weights: Dict[str, float] = None,
) -> List[MatchScore]:
    """Compute match scores for a student against all active internships."""
    internships = db.query(Internship).filter(
        Internship.status == InternshipStatus.ACTIVE
    ).all()

    results = []
    for internship in internships:
        # Delete existing score
        db.query(MatchScore).filter(
            MatchScore.student_id == student.id,
            MatchScore.internship_id == internship.id,
        ).delete()

        result = compute_match_score(db, student, internship, weights)

        match_record = MatchScore(
            student_id=student.id,
            internship_id=internship.id,
            skill_score=result["skill_score"],
            education_score=result["education_score"],
            location_score=result["location_score"],
            preference_score=result["preference_score"],
            academic_score=result["academic_score"],
            semantic_score=result["semantic_score"],
            overall_score=result["overall_score"],
            explanation=json.dumps(result["explanation"]),
        )
        db.add(match_record)
        results.append(match_record)

    db.commit()
    return results


def get_student_recommendations(
    db: Session,
    student: StudentProfile,
    limit: int = 20,
) -> List[Dict]:
    """Get top internship recommendations for a student."""
    # Ensure match scores exist
    existing = db.query(MatchScore).filter(
        MatchScore.student_id == student.id
    ).count()

    if existing == 0:
        compute_all_matches_for_student(db, student)

    matches = db.query(MatchScore).filter(
        MatchScore.student_id == student.id
    ).order_by(MatchScore.overall_score.desc()).limit(limit).all()

    recommendations = []
    for match in matches:
        internship = db.query(Internship).filter(Internship.id == match.internship_id).first()
        if not internship or internship.status != InternshipStatus.ACTIVE:
            continue

        company = db.query(Company).filter(Company.id == internship.company_id).first()

        explanation = {"reasons": [], "skill_gaps": []}
        if match.explanation:
            try:
                explanation = json.loads(match.explanation)
            except (json.JSONDecodeError, TypeError):
                explanation = {"reasons": [match.explanation], "skill_gaps": []}

        recommendations.append({
            "internship_id": internship.id,
            "title": internship.title,
            "company": company.organization_name if company else None,
            "domain": internship.domain,
            "location": internship.location,
            "match_score": match.overall_score,
            "skill_score": match.skill_score,
            "education_score": match.education_score,
            "location_score": match.location_score,
            "preference_score": match.preference_score,
            "academic_score": match.academic_score,
            "semantic_score": match.semantic_score,
            "explanation": explanation.get("reasons", []),
            "skill_gaps": explanation.get("skill_gaps", []),
        })

    return recommendations
