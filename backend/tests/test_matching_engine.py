import pytest
from types import SimpleNamespace
from app.services.matching_engine import (
    _compute_skill_score,
    _compute_education_score,
    _compute_location_score,
    _compute_preference_score,
    _compute_academic_score,
    _compute_semantic_score,
    _locations_in_same_state,
)


def test_skill_score_exact_match():
    student_skills = ["Python", "Machine Learning", "TensorFlow", "SQL"]
    internship = SimpleNamespace(
        required_skills=["Python", "Machine Learning"],
        preferred_skills=["TensorFlow", "Docker"]
    )
    result = _compute_skill_score(student_skills, internship)
    assert result["score"] >= 80
    assert "2 of 2 required skills match" in result["reasons"]
    assert len(result["gaps"]) == 0


def test_skill_score_partial_match():
    student_skills = ["Python"]
    internship = SimpleNamespace(
        required_skills=["Python", "Machine Learning", "TensorFlow"],
        preferred_skills=[]
    )
    result = _compute_skill_score(student_skills, internship)
    assert result["score"] < 50
    assert "1 of 3 required skills match" in result["reasons"]
    assert "Machine Learning" in result["gaps"]


def test_education_score_eligible():
    student = SimpleNamespace(degree="B.Tech", branch="CSE")
    internship = SimpleNamespace(
        eligible_degrees=["B.Tech", "B.E."],
        eligible_branches=["CSE", "IT"]
    )
    result = _compute_education_score(student, internship)
    assert result["score"] == 100
    assert any("B.Tech" in r for r in result["reasons"])
    assert any("CSE" in r for r in result["reasons"])


def test_education_score_ineligible_branch():
    student = SimpleNamespace(degree="B.Tech", branch="Civil")
    internship = SimpleNamespace(
        eligible_degrees=["B.Tech"],
        eligible_branches=["CSE", "IT"]
    )
    result = _compute_education_score(student, internship)
    assert result["score"] < 100
    assert any("Civil" in r for r in result["reasons"])


def test_location_score_exact_and_remote():
    student = SimpleNamespace(location="Bangalore", preferred_locations=["Hyderabad"])
    internship_exact = SimpleNamespace(location="Bangalore", work_mode="onsite")
    assert _compute_location_score(student, internship_exact)["score"] == 100

    internship_remote = SimpleNamespace(location="Delhi", work_mode="remote")
    assert _compute_location_score(student, internship_remote)["score"] == 90


def test_academic_score():
    student_high = SimpleNamespace(cgpa=9.2)
    student_low = SimpleNamespace(cgpa=6.0)
    internship = SimpleNamespace(minimum_cgpa=7.0)

    res_high = _compute_academic_score(student_high, internship)
    res_low = _compute_academic_score(student_low, internship)

    assert res_high["score"] == 100
    assert res_low["score"] < 50


def test_locations_in_same_state():
    assert _locations_in_same_state("mumbai", "pune") is True
    assert _locations_in_same_state("bangalore", "mysore") is True
    assert _locations_in_same_state("mumbai", "chennai") is False
