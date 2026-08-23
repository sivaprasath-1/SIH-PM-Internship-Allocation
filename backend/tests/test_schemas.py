import pytest
from pydantic import ValidationError
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    InternshipCreate,
    AllocationConfig,
)


def test_user_registration_schema_validation():
    valid = UserRegister(
        name="Aakash Verma",
        email="aakash.v@example.com",
        password="SecurePassword@123",
        role="student"
    )
    assert valid.role == "student"

    with pytest.raises(ValidationError):
        # Invalid role
        UserRegister(
            name="Invalid",
            email="invalid@example.com",
            password="pass",
            role="superhero"
        )


def test_internship_create_schema_validation():
    valid = InternshipCreate(
        title="AI Engineer Intern",
        domain="AI/ML",
        seats=3,
        work_mode="hybrid",
        required_skills=["Python", "TensorFlow"]
    )
    assert valid.seats == 3
    assert valid.work_mode == "hybrid"

    with pytest.raises(ValidationError):
        # Zero seats not allowed
        InternshipCreate(
            title="Invalid Seats",
            seats=0
        )


def test_allocation_config_weights_validation():
    config = AllocationConfig(
        skill_weight=0.40,
        semantic_weight=0.20,
        education_weight=0.15,
        location_weight=0.10,
        preference_weight=0.10,
        academic_weight=0.05
    )
    assert config.skill_weight == 0.40
    assert config.enforce_eligibility is True
