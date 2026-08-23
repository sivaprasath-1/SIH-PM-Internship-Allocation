import pytest
from types import SimpleNamespace
from app.services.allocation_engine import _check_eligibility, _solve_greedy
from app.schemas.schemas import AllocationConfig


def test_eligibility_checking():
    student_eligible = SimpleNamespace(cgpa=8.5, branch="CSE", degree="B.Tech")
    student_ineligible_cgpa = SimpleNamespace(cgpa=6.0, branch="CSE", degree="B.Tech")
    student_ineligible_branch = SimpleNamespace(cgpa=8.5, branch="Civil", degree="B.Tech")

    internship = SimpleNamespace(
        minimum_cgpa=7.0,
        eligible_branches=["CSE", "IT"],
        eligible_degrees=["B.Tech", "B.E."]
    )

    assert _check_eligibility(student_eligible, internship) is True
    assert _check_eligibility(student_ineligible_cgpa, internship) is False
    assert _check_eligibility(student_ineligible_branch, internship) is False


def test_greedy_allocation_capacity_and_single_assignment():
    # 3 students, 2 internships (Capacity: 1 each)
    students = [
        SimpleNamespace(id=1, cgpa=9.0, branch="CSE", degree="B.Tech"),
        SimpleNamespace(id=2, cgpa=8.5, branch="CSE", degree="B.Tech"),
        SimpleNamespace(id=3, cgpa=8.0, branch="CSE", degree="B.Tech"),
    ]

    internships = [
        SimpleNamespace(id=101, seats=1, minimum_cgpa=7.0, eligible_branches=["CSE"], eligible_degrees=["B.Tech"]),
        SimpleNamespace(id=102, seats=1, minimum_cgpa=7.0, eligible_branches=["CSE"], eligible_degrees=["B.Tech"]),
    ]

    config = AllocationConfig(enforce_eligibility=True, max_allocations_per_student=1)

    # Mock DB that returns match scores
    class MockQuery:
        def __init__(self, s_id, i_id):
            self.s_id = s_id
            self.i_id = i_id

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            # Student 1 gets 95% on 101, 80% on 102
            # Student 2 gets 90% on 101, 85% on 102
            # Student 3 gets 75% on 101, 70% on 102
            score_map = {
                (1, 101): 95.0, (1, 102): 80.0,
                (2, 101): 90.0, (2, 102): 85.0,
                (3, 101): 75.0, (3, 102): 70.0,
            }
            score = score_map.get((self.s_id, self.i_id), 0.0)
            return SimpleNamespace(overall_score=score, explanation='{"reasons": ["Good match"]}')

    class MockDB:
        def query(self, model):
            return MockQuery(1, 101)

    # Solve greedy
    allocations = _solve_greedy(MockDB(), students, internships, config)

    # Total allocations should equal available capacity (2)
    assert len(allocations) == 2

    # Each student assigned at most once
    allocated_students = [a[0] for a in allocations]
    assert len(allocated_students) == len(set(allocated_students))

    # Internship capacities respected (at most 1 per internship)
    allocated_internships = [a[1] for a in allocations]
    assert allocated_internships.count(101) <= 1
    assert allocated_internships.count(102) <= 1
