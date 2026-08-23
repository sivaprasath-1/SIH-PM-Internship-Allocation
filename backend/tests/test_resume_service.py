import pytest
from app.services.resume_service import (
    _extract_degree,
    _extract_branch,
    _extract_skills,
)


def test_resume_degree_extraction():
    text_btech = "Candidate holds a B.Tech in Computer Science from IIT Delhi."
    text_mca = "Completed MCA with focus on Web Development."

    assert _extract_degree(text_btech) == "B.Tech"
    assert _extract_degree(text_mca) == "MCA"


def test_resume_branch_extraction():
    text_cse = "Department of Computer Science and Engineering"
    text_ece = "Degree in Electronics and Communication Engineering (ECE)"

    assert _extract_branch(text_cse) == "CSE"
    assert _extract_branch(text_ece) == "ECE"


def test_resume_skill_dictionary_extraction():
    sample_resume = """
    TECHNICAL SKILLS:
    Languages: Python, TypeScript, SQL, Java
    Frameworks: FastAPI, React, Docker, Kubernetes
    Machine Learning: TensorFlow, PyTorch, Scikit-learn
    """

    skills = _extract_skills(sample_resume)

    expected = ["Python", "TypeScript", "SQL", "Java", "FastAPI", "React", "Docker", "Kubernetes", "TensorFlow", "PyTorch"]
    for exp in expected:
        assert exp in skills
