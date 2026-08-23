"""
End-to-End Verification Script for PM Internship Scheme
Tests all Student, Company, and Admin workflows, DB persistence, and error handling.
"""
import sys
import os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api"

def run_e2e():
    print("==================================================")
    print("🚀 STARTING FULL END-TO-END VERIFICATION")
    print("==================================================")

    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # ----------------------------------------------------
    # 1. AUTH & ERROR HANDLING
    # ----------------------------------------------------
    print("\n--- 1. Testing Auth & Error Handling ---")
    
    # Test invalid login
    res_bad_login = client.post("/auth/login", json={"email": "wrong@example.com", "password": "BadPassword"})
    assert res_bad_login.status_code == 401, f"Expected 401 on invalid login, got {res_bad_login.status_code}"
    print("✅ Proper 401 error on invalid credentials")

    # ----------------------------------------------------
    # 2. STUDENT WORKFLOW
    # ----------------------------------------------------
    import time
    timestamp = int(time.time())
    student_email = f"e2e.student.{timestamp}@example.com"
    student_pw = "StudentTest@123"

    # Register
    res_reg = client.post("/auth/register", json={
        "name": f"Arjun Sharma {timestamp}",
        "email": student_email,
        "password": student_pw,
        "role": "student"
    })
    if res_reg.status_code == 400: # Already registered from prior run
        res_login = client.post("/auth/login", json={"email": student_email, "password": student_pw})
        student_token = res_login.json()["access_token"]
        print(f"✅ Student logged in (existing account): {student_email}")
    else:
        assert res_reg.status_code == 200, f"Failed registration: {res_reg.text}"
        student_token = res_reg.json()["access_token"]
        print(f"✅ Student registration successful: {student_email}")

    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Test Duplicate Registration Prevention
    res_dup = client.post("/auth/register", json={
        "name": "Arjun Duplicate",
        "email": student_email,
        "password": student_pw,
        "role": "student"
    })
    assert res_dup.status_code == 400, "Duplicate registration was not blocked"
    print("✅ Duplicate registration blocked with 400 Bad Request")

    # Get & Update Student Profile
    res_prof = client.get("/students/profile", headers=student_headers)
    assert res_prof.status_code == 200
    print("✅ Fetched student profile")

    res_upd = client.put("/students/profile", headers=student_headers, json={
        "phone": "+919876543210",
        "gender": "Male",
        "degree": "B.Tech",
        "branch": "CSE",
        "college": "IIT Delhi",
        "graduation_year": 2026,
        "cgpa": 8.9,
        "location": "Delhi",
        "preferred_locations": ["Bangalore", "Delhi", "Hyderabad"],
        "preferred_domains": ["AI/ML", "Web Development"],
        "bio": "Passionate computer science student interested in NLP and distributed systems."
    })
    assert res_upd.status_code == 200
    assert res_upd.json()["branch"] == "CSE"
    assert res_upd.json()["cgpa"] == 8.9
    print("✅ Updated student profile (Branch: CSE, CGPA: 8.9, College: IIT Delhi)")

    # Add Skills
    res_skill1 = client.post("/students/skills", headers=student_headers, json={"name": "Python", "proficiency_level": "expert"})
    assert res_skill1.status_code == 200
    res_skill2 = client.post("/students/skills", headers=student_headers, json={"name": "React", "proficiency_level": "advanced"})
    assert res_skill2.status_code == 200
    res_skill3 = client.post("/students/skills", headers=student_headers, json={"name": "Docker", "proficiency_level": "intermediate"})
    assert res_skill3.status_code == 200
    skill3_id = res_skill3.json()["id"]
    print("✅ Added skills: Python (expert), React (advanced), Docker (intermediate)")

    # Remove Skill
    res_del_skill = client.delete(f"/students/skills/{skill3_id}", headers=student_headers)
    assert res_del_skill.status_code == 200
    print("✅ Removed temporary skill")

    # Browse Internships
    res_interns = client.get("/internships?domain=AI/ML")
    assert res_interns.status_code == 200
    internships_list = res_interns.json()
    assert len(internships_list) > 0
    target_internship = internships_list[0]
    target_internship_id = target_internship["id"]
    print(f"✅ Browsed internships: found {len(internships_list)} AI/ML openings. Target: '{target_internship['title']}' (ID: {target_internship_id})")

    # Recommendations
    res_recs = client.get("/students/recommendations", headers=student_headers)
    assert res_recs.status_code == 200
    recs = res_recs.json()
    print(f"✅ AI Recommendations generated: {len(recs)} matching opportunities")

    # Apply to Internship
    res_apply = client.post(f"/internships/{target_internship_id}/apply", headers=student_headers)
    if res_apply.status_code == 400 and "already applied" in res_apply.text.lower():
        print(f"✅ Application check: already applied to '{target_internship['title']}'")
    else:
        assert res_apply.status_code == 200, f"Application failed: {res_apply.text}"
        print(f"✅ Successfully applied to '{target_internship['title']}'")

    # Duplicate Application Prevention
    res_dup_apply = client.post(f"/internships/{target_internship_id}/apply", headers=student_headers)
    assert res_dup_apply.status_code == 400
    print("✅ Duplicate application correctly rejected")

    # View Applications
    res_my_apps = client.get("/students/applications", headers=student_headers)
    assert res_my_apps.status_code == 200
    print(f"✅ Student application tracker: {len(res_my_apps.json())} active applications")

    # Notifications
    res_notifs = client.get("/notifications", headers=student_headers)
    assert res_notifs.status_code == 200
    notifs = res_notifs.json()
    print(f"✅ Notifications list: {len(notifs)} received")
    if notifs:
        res_read = client.post(f"/notifications/{notifs[0]['id']}/read", headers=student_headers)
        assert res_read.status_code == 200
        print(f"✅ Marked notification #{notifs[0]['id']} as read")

    # ----------------------------------------------------
    # 3. COMPANY WORKFLOW
    # ----------------------------------------------------
    print("\n--- 3. Testing Company Workflow ---")

    company_email = "hr@technovasolutions.in"
    company_pw = "Company@123"

    res_comp_login = client.post("/auth/login", json={"email": company_email, "password": company_pw})
    assert res_comp_login.status_code == 200
    comp_token = res_comp_login.json()["access_token"]
    comp_headers = {"Authorization": f"Bearer {comp_token}"}
    print(f"✅ Company login successful: {company_email}")

    # View & Update Company Profile
    res_c_prof = client.get("/companies/profile", headers=comp_headers)
    assert res_c_prof.status_code == 200
    print(f"✅ Fetched company profile: {res_c_prof.json()['organization_name']}")

    res_c_upd = client.put("/companies/profile", headers=comp_headers, json={
        "organization_name": "TechNova Solutions India",
        "description": "Leading enterprise AI and cloud engineering company.",
        "industry": "Information Technology",
        "location": "Bangalore",
        "website": "https://technova.in"
    })
    assert res_c_upd.status_code == 200
    print("✅ Updated company profile")

    # Create Internship
    new_intern_title = "Cloud & AI Research Engineer Intern (E2E Test)"
    res_create_i = client.post("/companies/internships", headers=comp_headers, json={
        "title": new_intern_title,
        "description": "Work with our distributed systems and LLM research teams.",
        "domain": "AI/ML",
        "location": "Bangalore",
        "work_mode": "hybrid",
        "duration": "6 months",
        "stipend": 30000,
        "seats": 4,
        "minimum_cgpa": 7.5,
        "eligible_degrees": ["B.Tech", "M.Tech"],
        "eligible_branches": ["CSE", "IT", "ECE"],
        "required_skills": ["Python", "Docker", "Machine Learning"],
        "preferred_skills": ["Kubernetes", "PyTorch"]
    })
    assert res_create_i.status_code == 200
    created_intern_id = res_create_i.json()["id"]
    print(f"✅ Created internship: '{new_intern_title}' (ID: {created_intern_id}, Seats: 4, Stipend: ₹30,000)")

    # View Company Internships & Applications
    res_c_interns = client.get("/companies/internships", headers=comp_headers)
    assert res_c_interns.status_code == 200
    print(f"✅ Fetched company internships: {len(res_c_interns.json())} active postings")

    res_c_apps = client.get(f"/companies/internships/{target_internship_id}/applications", headers=comp_headers)
    print(f"✅ Fetched applicants for internship #{target_internship_id}: {len(res_c_apps.json())} candidate(s)")

    # View Recommended Candidates
    res_candidates = client.get("/companies/candidates", headers=comp_headers)
    assert res_candidates.status_code == 200
    print(f"✅ Candidate matching pool: {len(res_candidates.json())} recommended candidates")

    # Clean up test internship
    res_del_i = client.delete(f"/companies/internships/{created_intern_id}", headers=comp_headers)
    assert res_del_i.status_code == 200
    print(f"✅ Deleted temporary test internship #{created_intern_id}")

    # ----------------------------------------------------
    # 4. ADMIN WORKFLOW
    # ----------------------------------------------------
    print("\n--- 4. Testing Admin Workflow ---")

    admin_email = "admin@pmias.gov.in"
    admin_pw = "Admin@123"

    res_admin_login = client.post("/auth/login", json={"email": admin_email, "password": admin_pw})
    assert res_admin_login.status_code == 200
    admin_token = res_admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"✅ Admin login successful: {admin_email}")

    # Dashboard Stats
    res_dash = client.get("/admin/dashboard", headers=admin_headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    print(f"✅ Admin Dashboard: {dash_data['total_students']} Students, {dash_data['total_companies']} Companies, {dash_data['total_internships']} Internships, {dash_data['total_seats']} Seats")

    # Students Directory
    res_adm_students = client.get("/admin/students?branch=CSE", headers=admin_headers)
    assert res_adm_students.status_code == 200
    print(f"✅ Filtered students directory (CSE): {res_adm_students.json()['total']} matches")

    # Companies Directory & Verification
    res_adm_comps = client.get("/admin/companies", headers=admin_headers)
    assert res_adm_comps.status_code == 200
    companies = res_adm_comps.json()["companies"]
    print(f"✅ Companies directory: {len(companies)} organizations")
    if companies:
        first_comp_id = companies[0]["id"]
        res_verify = client.post(f"/admin/companies/{first_comp_id}/verify?action=verified", headers=admin_headers)
        assert res_verify.status_code == 200
        print(f"✅ Verified organization #{first_comp_id}")

    # Internships Directory
    res_adm_interns = client.get("/admin/internships", headers=admin_headers)
    assert res_adm_interns.status_code == 200
    print(f"✅ Admin internships directory: {res_adm_interns.json()['total']} listings")

    # Applications Directory
    res_adm_apps = client.get("/admin/applications", headers=admin_headers)
    assert res_adm_apps.status_code == 200
    print(f"✅ Admin applications log: {res_adm_apps.json()['total']} submissions")

    # Run AI Allocation Engine
    print("\n⚡ Running AI Constraint Allocation Optimization...")
    res_alloc_run = client.post("/admin/allocation/run", headers=admin_headers, json={
        "skill_weight": 0.35,
        "semantic_weight": 0.20,
        "education_weight": 0.15,
        "location_weight": 0.10,
        "preference_weight": 0.10,
        "academic_weight": 0.10,
        "enforce_eligibility": True,
        "max_allocations_per_student": 1
    })
    assert res_alloc_run.status_code == 200
    alloc_result = res_alloc_run.json()
    print(f"✅ Optimization Engine Complete: Status={alloc_result['status']}, Allocated={alloc_result['total_allocations']}, Unallocated={alloc_result['unallocated_students']}, FirstChoiceRate={alloc_result['first_choice_rate']}%")

    # Allocation Statistics & Fairness
    res_stats = client.get("/admin/allocation/statistics", headers=admin_headers)
    assert res_stats.status_code == 200
    stat_data = res_stats.json()
    print(f"✅ Allocation Fairness Stats: Seat Utilization={stat_data['seat_utilization']}%, Avg Match={stat_data['avg_match_score']}%, Branches={list(stat_data['by_branch'].keys())}")

    # Unallocated Students & Unfilled Internships
    res_unalloc = client.get("/admin/allocation/unallocated-students", headers=admin_headers)
    assert res_unalloc.status_code == 200
    print(f"✅ Unallocated candidates tracker: {len(res_unalloc.json())} pending")

    res_unfilled = client.get("/admin/allocation/unfilled-internships", headers=admin_headers)
    assert res_unfilled.status_code == 200
    print(f"✅ Unfilled openings tracker: {len(res_unfilled.json())} openings with open seats")

    # Audit Logs
    res_logs = client.get("/admin/audit-logs", headers=admin_headers)
    assert res_logs.status_code == 200
    print(f"✅ System audit trail: {res_logs.json()['total']} logged administrative actions")

    # ----------------------------------------------------
    # 5. ALLOCATION ACCEPT/REJECT (STUDENT)
    # ----------------------------------------------------
    print("\n--- 5. Testing Student Allocation Response ---")
    res_my_allocs = client.get("/students/allocations", headers=student_headers)
    assert res_my_allocs.status_code == 200
    student_allocations = res_my_allocs.json()
    if student_allocations:
        my_alloc = student_allocations[0]
        print(f"✅ Student allocated to: '{my_alloc['internship_title']}' (Score: {my_alloc['match_score']}%)")
        res_accept = client.post(f"/students/allocations/{my_alloc['id']}/accept", headers=student_headers)
        assert res_accept.status_code == 200
        print("✅ Student successfully accepted allocation offer")

    print("\n==================================================")
    print("🎉 ALL END-TO-END WORKFLOWS VERIFIED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_e2e()
