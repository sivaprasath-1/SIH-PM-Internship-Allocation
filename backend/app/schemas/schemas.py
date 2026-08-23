from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ==================== AUTH ====================

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(..., pattern="^(student|company|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== STUDENT ====================

class StudentProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    location: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    preferred_domains: Optional[List[str]] = None
    bio: Optional[str] = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    location: Optional[str] = None
    preferred_locations: Optional[List[str]] = []
    preferred_domains: Optional[List[str]] = []
    bio: Optional[str] = None
    resume_url: Optional[str] = None
    skills: Optional[List["StudentSkillResponse"]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SkillAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    proficiency_level: str = Field("intermediate", pattern="^(beginner|intermediate|advanced|expert)$")


class StudentSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    proficiency_level: str

    class Config:
        from_attributes = True


# ==================== COMPANY ====================

class CompanyProfileUpdate(BaseModel):
    organization_name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    user_id: int
    organization_name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    verification_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== INTERNSHIP ====================

class InternshipCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    work_mode: str = Field("onsite", pattern="^(onsite|remote|hybrid)$")
    duration: Optional[str] = None
    stipend: Optional[float] = Field(None, ge=0)
    seats: int = Field(1, ge=1)
    application_deadline: Optional[datetime] = None
    minimum_cgpa: Optional[float] = Field(None, ge=0, le=10)
    eligible_degrees: Optional[List[str]] = []
    eligible_branches: Optional[List[str]] = []
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []


class InternshipUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    duration: Optional[str] = None
    stipend: Optional[float] = None
    seats: Optional[int] = None
    application_deadline: Optional[datetime] = None
    minimum_cgpa: Optional[float] = None
    eligible_degrees: Optional[List[str]] = None
    eligible_branches: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    status: Optional[str] = None


class InternshipResponse(BaseModel):
    id: int
    company_id: int
    company_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    work_mode: str
    duration: Optional[str] = None
    stipend: Optional[float] = None
    seats: int
    filled_seats: Optional[int] = 0
    application_deadline: Optional[datetime] = None
    minimum_cgpa: Optional[float] = None
    eligible_degrees: Optional[List[str]] = []
    eligible_branches: Optional[List[str]] = []
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    status: str
    application_count: Optional[int] = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== APPLICATION ====================

class ApplicationResponse(BaseModel):
    id: int
    student_id: int
    internship_id: int
    student_name: Optional[str] = None
    internship_title: Optional[str] = None
    company_name: Optional[str] = None
    status: str
    match_score: Optional[float] = None
    applied_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== MATCH SCORE ====================

class MatchScoreResponse(BaseModel):
    id: int
    student_id: int
    internship_id: int
    internship_title: Optional[str] = None
    company_name: Optional[str] = None
    skill_score: float
    education_score: float
    location_score: float
    preference_score: float
    academic_score: float
    semantic_score: float
    overall_score: float
    explanation: Optional[List[str]] = []
    skill_gaps: Optional[List[str]] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    internship: InternshipResponse
    match: MatchScoreResponse


# ==================== ALLOCATION ====================

class AllocationResponse(BaseModel):
    id: int
    student_id: int
    internship_id: int
    student_name: Optional[str] = None
    internship_title: Optional[str] = None
    company_name: Optional[str] = None
    match_score: float
    allocation_status: str
    allocated_at: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    student_response: Optional[str] = None
    allocation_reason: Optional[str] = None

    class Config:
        from_attributes = True


class AllocationConfig(BaseModel):
    skill_weight: float = Field(0.35, ge=0, le=1)
    semantic_weight: float = Field(0.20, ge=0, le=1)
    education_weight: float = Field(0.15, ge=0, le=1)
    location_weight: float = Field(0.10, ge=0, le=1)
    preference_weight: float = Field(0.10, ge=0, le=1)
    academic_weight: float = Field(0.10, ge=0, le=1)
    enforce_eligibility: bool = True
    max_allocations_per_student: int = 1


class AllocationRunResponse(BaseModel):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    total_students: int
    total_internships: int
    total_allocations: int
    unallocated_students: int
    unfilled_seats: Optional[int] = 0
    avg_match_score: Optional[float] = 0.0
    first_choice_rate: Optional[float] = 0.0

    class Config:
        from_attributes = True


class AllocationStatistics(BaseModel):
    total_students: int
    total_internships: int
    total_seats: int
    eligible_students: int
    allocated_students: int
    unallocated_students: int
    allocation_percentage: float
    avg_match_score: float
    first_choice_rate: float
    seat_utilization: float
    by_location: Optional[dict] = {}
    by_branch: Optional[dict] = {}
    by_domain: Optional[dict] = {}
    by_gender: Optional[dict] = {}
    skill_demand: Optional[List[dict]] = []


# ==================== NOTIFICATION ====================

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: Optional[str] = None
    type: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== ADMIN ====================

class DashboardStats(BaseModel):
    total_students: int
    total_companies: int
    total_internships: int
    total_seats: int
    total_applications: int
    allocated_students: int
    unallocated_students: int
    allocation_percentage: float
    avg_match_score: float
    verified_companies: int
    active_internships: int
    students_by_branch: dict
    internships_by_domain: dict
    recent_applications: List[ApplicationResponse]


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== RESUME ====================

class ResumeAnalysisResponse(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    skills: List[str] = []
    projects: List[str] = []
    experience: List[str] = []
    certifications: List[str] = []


# Forward reference resolution
TokenResponse.model_rebuild()
StudentProfileResponse.model_rebuild()
