"""
Seed Data Script
Creates realistic demo data for the PM Internship Smart Allocation Engine.
Run: py -3 -m scripts.seed
"""
import sys
import os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.student import StudentProfile
from app.models.company import Company, VerificationStatus
from app.models.internship import Internship, InternshipStatus, WorkMode
from app.models.skill import Skill, StudentSkill
from app.models.application import Application, ApplicationStatus
from app.models.allocation import Allocation, AllocationRun
from app.models.match_score import MatchScore
from app.models.notification import Notification, NotificationType
from app.auth.auth_service import hash_password

# ==================== DATA ====================

SKILLS_DATA = {
    "Programming Languages": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "R", "Kotlin", "Swift"],
    "Web Development": ["React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI", "HTML", "CSS", "Next.js", "Spring Boot"],
    "Data Science & AI/ML": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Pandas", "NumPy", "Scikit-learn", "Data Analysis"],
    "Database": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Firebase", "Elasticsearch"],
    "Cloud & DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Linux", "Git", "Jenkins"],
    "Cybersecurity": ["Network Security", "Penetration Testing", "Cryptography", "OWASP", "Ethical Hacking"],
    "Embedded & IoT": ["Embedded Systems", "IoT", "Arduino", "Raspberry Pi", "MQTT", "RTOS"],
    "Tools": ["Git", "Jira", "Postman", "Figma", "VS Code", "Jupyter", "Power BI", "Tableau"],
}

COLLEGES = [
    "IIT Delhi", "IIT Bombay", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
    "NIT Trichy", "NIT Warangal", "NIT Surathkal", "NIT Calicut", "NIT Rourkela",
    "BITS Pilani", "VIT Vellore", "SRM Chennai", "Manipal Institute of Technology",
    "DTU Delhi", "NSUT Delhi", "IIIT Hyderabad", "IIIT Bangalore",
    "Anna University", "Jadavpur University", "BMS College Bangalore",
    "RV College Bangalore", "PSG Tech Coimbatore", "Amrita Vishwa Vidyapeetham",
    "KIIT Bhubaneswar",
]

LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Kochi", "Chandigarh", "Noida", "Gurgaon", "Coimbatore",
]

BRANCHES = ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil"]
DEGREES = ["B.Tech", "B.E.", "M.Tech", "MCA", "B.Sc"]
DOMAINS = ["AI/ML", "Web Development", "Cybersecurity", "Data Science", "Cloud Computing", "Embedded Systems", "Software Engineering", "IoT"]
GENDERS = ["Male", "Female", "Other"]

FIRST_NAMES_M = ["Rahul", "Amit", "Vikram", "Arjun", "Rohit", "Aakash", "Siddharth", "Nikhil", "Kartik", "Pranav",
                  "Aditya", "Varun", "Karan", "Manish", "Deepak", "Rajesh", "Sachin", "Harsh", "Gaurav", "Mohit",
                  "Ankit", "Shubham", "Tushar", "Dhruv", "Rohan"]
FIRST_NAMES_F = ["Priya", "Ananya", "Kavya", "Shreya", "Neha", "Pooja", "Divya", "Sneha", "Riya", "Meera",
                  "Tanvi", "Ishita", "Nandini", "Swati", "Aisha", "Sanya", "Vedika", "Ritika", "Khushi", "Mira",
                  "Ayesha", "Simran", "Aditi", "Bhavna", "Charvi"]
LAST_NAMES = ["Kumar", "Sharma", "Singh", "Patel", "Gupta", "Reddy", "Nair", "Iyer", "Joshi", "Verma",
              "Mishra", "Das", "Srinivasan", "Bhat", "Agarwal", "Mehta", "Chauhan", "Rao", "Pillai", "Menon",
              "Choudhury", "Banerjee", "Deshpande", "Kulkarni", "Tiwari"]

COMPANIES_DATA = [
    {"name": "TechNova Solutions", "industry": "Information Technology", "location": "Bangalore", "website": "https://technova.in", "description": "Leading IT solutions provider specializing in AI, cloud computing, and enterprise software development."},
    {"name": "DataSphere Analytics", "industry": "Data Analytics", "location": "Hyderabad", "website": "https://datasphere.in", "description": "Premier data analytics firm delivering actionable insights through ML and big data technologies."},
    {"name": "CyberShield India", "industry": "Cybersecurity", "location": "Delhi", "website": "https://cybershield.in", "description": "India's trusted cybersecurity company providing threat detection, penetration testing, and security consulting."},
    {"name": "CloudMatrix Technologies", "industry": "Cloud Computing", "location": "Pune", "website": "https://cloudmatrix.in", "description": "Cloud infrastructure and DevOps specialists helping enterprises modernize their IT operations."},
    {"name": "GreenTech Innovations", "industry": "Clean Technology", "location": "Chennai", "website": "https://greentech.in", "description": "Sustainable technology company developing IoT-based environmental monitoring and clean energy solutions."},
    {"name": "FinEdge Systems", "industry": "Fintech", "location": "Mumbai", "website": "https://finedge.in", "description": "Fintech startup building next-generation payment systems and financial analytics platforms."},
    {"name": "RoboWorks India", "industry": "Robotics & Automation", "location": "Bangalore", "website": "https://roboworks.in", "description": "Cutting-edge robotics and automation company developing intelligent manufacturing solutions."},
    {"name": "MedAI Healthcare", "industry": "Healthcare Technology", "location": "Hyderabad", "website": "https://medai.in", "description": "Healthcare AI company building diagnostic tools and patient management systems."},
    {"name": "EduTech Bharat", "industry": "Education Technology", "location": "Noida", "website": "https://edutechbharat.in", "description": "EdTech platform revolutionizing learning through adaptive AI and personalized content delivery."},
    {"name": "SpaceView Systems", "industry": "Aerospace & Defense", "location": "Bangalore", "website": "https://spaceview.in", "description": "Aerospace technology company developing satellite communication and geospatial analysis tools."},
]

INTERNSHIPS_DATA = [
    {"title": "AI/ML Research Intern", "domain": "AI/ML", "required_skills": ["Python", "Machine Learning", "TensorFlow", "Data Analysis", "NumPy"], "preferred_skills": ["Deep Learning", "PyTorch", "NLP"], "branches": ["CSE", "IT", "ECE"], "cgpa": 7.0, "seats": 5, "stipend": 25000, "duration": "6 months", "work_mode": "hybrid"},
    {"title": "Full Stack Web Developer Intern", "domain": "Web Development", "required_skills": ["React", "Node.js", "JavaScript", "HTML", "CSS"], "preferred_skills": ["TypeScript", "MongoDB", "Docker"], "branches": ["CSE", "IT"], "cgpa": 6.5, "seats": 8, "stipend": 20000, "duration": "3 months", "work_mode": "onsite"},
    {"title": "Cybersecurity Analyst Intern", "domain": "Cybersecurity", "required_skills": ["Network Security", "Linux", "Python", "OWASP"], "preferred_skills": ["Penetration Testing", "Cryptography"], "branches": ["CSE", "IT", "ECE"], "cgpa": 7.0, "seats": 3, "stipend": 22000, "duration": "6 months", "work_mode": "onsite"},
    {"title": "Data Science Intern", "domain": "Data Science", "required_skills": ["Python", "SQL", "Pandas", "Machine Learning", "Data Analysis"], "preferred_skills": ["Tableau", "Power BI", "Scikit-learn"], "branches": ["CSE", "IT", "ECE"], "cgpa": 6.5, "seats": 6, "stipend": 22000, "duration": "4 months", "work_mode": "hybrid"},
    {"title": "Cloud DevOps Intern", "domain": "Cloud Computing", "required_skills": ["AWS", "Docker", "Linux", "CI/CD", "Git"], "preferred_skills": ["Kubernetes", "Jenkins", "Azure"], "branches": ["CSE", "IT"], "cgpa": 6.0, "seats": 4, "stipend": 25000, "duration": "6 months", "work_mode": "remote"},
    {"title": "Embedded Systems Intern", "domain": "Embedded Systems", "required_skills": ["C", "C++", "Embedded Systems", "Arduino"], "preferred_skills": ["RTOS", "IoT", "Raspberry Pi"], "branches": ["ECE", "EEE", "CSE"], "cgpa": 6.5, "seats": 3, "stipend": 18000, "duration": "3 months", "work_mode": "onsite"},
    {"title": "Backend Developer Intern", "domain": "Software Engineering", "required_skills": ["Python", "FastAPI", "PostgreSQL", "Git"], "preferred_skills": ["Docker", "Redis", "CI/CD"], "branches": ["CSE", "IT"], "cgpa": 6.0, "seats": 5, "stipend": 20000, "duration": "4 months", "work_mode": "hybrid"},
    {"title": "IoT Solutions Intern", "domain": "IoT", "required_skills": ["IoT", "Python", "MQTT", "Arduino", "Embedded Systems"], "preferred_skills": ["Raspberry Pi", "AWS", "Machine Learning"], "branches": ["ECE", "EEE", "CSE", "IT"], "cgpa": 6.0, "seats": 3, "stipend": 18000, "duration": "3 months", "work_mode": "onsite"},
    {"title": "Mobile App Developer Intern", "domain": "Web Development", "required_skills": ["React", "JavaScript", "TypeScript", "Git"], "preferred_skills": ["Kotlin", "Swift", "Firebase"], "branches": ["CSE", "IT"], "cgpa": 6.5, "seats": 4, "stipend": 20000, "duration": "3 months", "work_mode": "remote"},
    {"title": "Computer Vision Research Intern", "domain": "AI/ML", "required_skills": ["Python", "Computer Vision", "Deep Learning", "TensorFlow"], "preferred_skills": ["PyTorch", "NumPy", "Data Analysis"], "branches": ["CSE", "ECE"], "cgpa": 7.5, "seats": 2, "stipend": 28000, "duration": "6 months", "work_mode": "onsite"},
    {"title": "NLP Engineer Intern", "domain": "AI/ML", "required_skills": ["Python", "NLP", "Machine Learning", "Deep Learning"], "preferred_skills": ["TensorFlow", "PyTorch", "Scikit-learn"], "branches": ["CSE", "IT"], "cgpa": 7.0, "seats": 3, "stipend": 26000, "duration": "6 months", "work_mode": "hybrid"},
    {"title": "Frontend Developer Intern", "domain": "Web Development", "required_skills": ["React", "JavaScript", "HTML", "CSS", "TypeScript"], "preferred_skills": ["Next.js", "Figma", "Vue.js"], "branches": ["CSE", "IT"], "cgpa": 6.0, "seats": 6, "stipend": 18000, "duration": "3 months", "work_mode": "remote"},
    {"title": "Data Engineering Intern", "domain": "Data Science", "required_skills": ["Python", "SQL", "AWS", "Data Analysis"], "preferred_skills": ["Docker", "Kubernetes", "Redis"], "branches": ["CSE", "IT", "ECE"], "cgpa": 6.5, "seats": 4, "stipend": 22000, "duration": "4 months", "work_mode": "hybrid"},
    {"title": "Blockchain Developer Intern", "domain": "Software Engineering", "required_skills": ["JavaScript", "Python", "Git"], "preferred_skills": ["Docker", "Node.js", "React"], "branches": ["CSE", "IT"], "cgpa": 7.0, "seats": 2, "stipend": 25000, "duration": "6 months", "work_mode": "remote"},
    {"title": "QA Automation Intern", "domain": "Software Engineering", "required_skills": ["Python", "Git", "SQL", "Linux"], "preferred_skills": ["Jenkins", "Docker", "CI/CD"], "branches": ["CSE", "IT", "ECE"], "cgpa": 6.0, "seats": 4, "stipend": 16000, "duration": "3 months", "work_mode": "onsite"},
    {"title": "Robotics Engineering Intern", "domain": "Embedded Systems", "required_skills": ["C++", "Python", "Embedded Systems"], "preferred_skills": ["Arduino", "Raspberry Pi", "RTOS"], "branches": ["ECE", "EEE", "Mechanical"], "cgpa": 6.5, "seats": 2, "stipend": 20000, "duration": "6 months", "work_mode": "onsite"},
    {"title": "Healthcare AI Intern", "domain": "AI/ML", "required_skills": ["Python", "Machine Learning", "Deep Learning", "Data Analysis"], "preferred_skills": ["TensorFlow", "Computer Vision", "NLP"], "branches": ["CSE", "IT", "ECE"], "cgpa": 7.0, "seats": 3, "stipend": 24000, "duration": "6 months", "work_mode": "hybrid"},
    {"title": "Network Security Intern", "domain": "Cybersecurity", "required_skills": ["Network Security", "Linux", "Python"], "preferred_skills": ["Ethical Hacking", "Penetration Testing", "OWASP"], "branches": ["CSE", "IT", "ECE"], "cgpa": 6.5, "seats": 3, "stipend": 20000, "duration": "4 months", "work_mode": "onsite"},
    {"title": "Cloud Solutions Architect Intern", "domain": "Cloud Computing", "required_skills": ["AWS", "Azure", "Docker", "Linux"], "preferred_skills": ["Kubernetes", "CI/CD", "GCP"], "branches": ["CSE", "IT"], "cgpa": 7.0, "seats": 2, "stipend": 28000, "duration": "6 months", "work_mode": "remote"},
    {"title": "Big Data Analytics Intern", "domain": "Data Science", "required_skills": ["Python", "SQL", "Data Analysis", "Machine Learning"], "preferred_skills": ["Pandas", "NumPy", "Tableau", "Power BI"], "branches": ["CSE", "IT", "ECE"], "cgpa": 6.5, "seats": 4, "stipend": 22000, "duration": "4 months", "work_mode": "hybrid"},
    {"title": "DevOps Intern", "domain": "Cloud Computing", "required_skills": ["Linux", "Docker", "Git", "CI/CD"], "preferred_skills": ["Kubernetes", "AWS", "Jenkins"], "branches": ["CSE", "IT"], "cgpa": 6.0, "seats": 5, "stipend": 20000, "duration": "3 months", "work_mode": "hybrid"},
    {"title": "UI/UX Design Intern", "domain": "Web Development", "required_skills": ["Figma", "HTML", "CSS", "JavaScript"], "preferred_skills": ["React", "Vue.js", "TypeScript"], "branches": ["CSE", "IT"], "cgpa": 6.0, "seats": 3, "stipend": 16000, "duration": "3 months", "work_mode": "remote"},
    {"title": "Edge Computing Intern", "domain": "IoT", "required_skills": ["Python", "IoT", "Linux", "MQTT"], "preferred_skills": ["Docker", "AWS", "Embedded Systems"], "branches": ["CSE", "IT", "ECE", "EEE"], "cgpa": 6.5, "seats": 2, "stipend": 20000, "duration": "4 months", "work_mode": "onsite"},
    {"title": "Fintech Software Intern", "domain": "Software Engineering", "required_skills": ["Python", "JavaScript", "SQL", "Git"], "preferred_skills": ["React", "Node.js", "Docker", "Redis"], "branches": ["CSE", "IT"], "cgpa": 7.0, "seats": 4, "stipend": 25000, "duration": "6 months", "work_mode": "hybrid"},
    {"title": "Satellite Data Analyst Intern", "domain": "Data Science", "required_skills": ["Python", "Data Analysis", "Machine Learning"], "preferred_skills": ["NumPy", "Pandas", "GCP"], "branches": ["CSE", "ECE", "IT"], "cgpa": 7.5, "seats": 2, "stipend": 30000, "duration": "6 months", "work_mode": "onsite"},
]


def seed():
    """Seed the database with demo data."""
    db = SessionLocal()

    try:
        print("🌱 Starting database seed...")

        # Check if already seeded
        if db.query(User).count() > 0:
            print("⚠️  Database already has data. Clearing...")
            # Clear all tables in reverse dependency order
            db.query(Notification).delete()
            db.query(Application).delete()
            db.query(Allocation).delete()
            db.query(AllocationRun).delete()
            db.query(MatchScore).delete()
            db.query(StudentSkill).delete()
            db.query(Internship).delete()
            db.query(Company).delete()
            db.query(StudentProfile).delete()
            db.query(Skill).delete()
            db.query(User).delete()
            db.commit()

        # 1. Create skills
        print("📚 Creating skills...")
        skill_objects = {}
        for category, skill_names in SKILLS_DATA.items():
            for name in skill_names:
                if name not in skill_objects:
                    skill = Skill(name=name, category=category)
                    db.add(skill)
                    db.flush()
                    skill_objects[name] = skill
        db.commit()
        print(f"   Created {len(skill_objects)} skills")

        # 2. Create admin user
        print("👤 Creating admin user...")
        admin_user = User(
            name="System Administrator",
            email="admin@pmias.gov.in",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
        )
        db.add(admin_user)
        db.commit()

        # 3. Create companies
        print("🏢 Creating companies...")
        company_users = []
        company_objects = []
        for i, comp_data in enumerate(COMPANIES_DATA):
            user = User(
                name=comp_data["name"],
                email=f"hr@{comp_data['name'].lower().replace(' ', '')}.in",
                password_hash=hash_password("Company@123"),
                role=UserRole.COMPANY,
            )
            db.add(user)
            db.flush()

            company = Company(
                user_id=user.id,
                organization_name=comp_data["name"],
                description=comp_data["description"],
                industry=comp_data["industry"],
                location=comp_data["location"],
                website=comp_data["website"],
                verification_status=VerificationStatus.VERIFIED if i < 8 else VerificationStatus.PENDING,
            )
            db.add(company)
            db.flush()

            company_users.append(user)
            company_objects.append(company)
        db.commit()
        print(f"   Created {len(company_objects)} companies")

        # 4. Create internships
        print("💼 Creating internships...")
        internship_objects = []
        for i, intern_data in enumerate(INTERNSHIPS_DATA):
            company = company_objects[i % len(company_objects)]
            location = random.choice(LOCATIONS)

            internship = Internship(
                company_id=company.id,
                title=intern_data["title"],
                description=f"{intern_data['title']} at {company.organization_name}. "
                           f"Work on cutting-edge projects in {intern_data['domain']}. "
                           f"Gain hands-on experience with {', '.join(intern_data['required_skills'][:3])}.",
                domain=intern_data["domain"],
                location=location,
                work_mode=WorkMode(intern_data["work_mode"]),
                duration=intern_data["duration"],
                stipend=intern_data["stipend"],
                seats=intern_data["seats"],
                application_deadline=datetime.utcnow() + timedelta(days=random.randint(30, 90)),
                minimum_cgpa=intern_data["cgpa"],
                eligible_degrees=["B.Tech", "B.E.", "M.Tech", "MCA"],
                eligible_branches=intern_data["branches"],
                required_skills=intern_data["required_skills"],
                preferred_skills=intern_data["preferred_skills"],
                status=InternshipStatus.ACTIVE,
            )
            db.add(internship)
            db.flush()
            internship_objects.append(internship)
        db.commit()
        print(f"   Created {len(internship_objects)} internships")

        # 5. Create students
        print("🎓 Creating students...")
        student_objects = []
        for i in range(50):
            is_female = i >= 25
            first_name = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
            last_name = random.choice(LAST_NAMES)
            name = f"{first_name} {last_name}"

            # Ensure unique email
            email = f"{first_name.lower()}.{last_name.lower()}{i}@student.com"

            user = User(
                name=name,
                email=email,
                password_hash=hash_password("Student@123"),
                role=UserRole.STUDENT,
            )
            db.add(user)
            db.flush()

            branch = random.choice(BRANCHES)
            location = random.choice(LOCATIONS)
            preferred_locs = random.sample(LOCATIONS, random.randint(1, 3))
            preferred_doms = random.sample(DOMAINS, random.randint(1, 3))

            profile = StudentProfile(
                user_id=user.id,
                date_of_birth=date(random.randint(2000, 2004), random.randint(1, 12), random.randint(1, 28)),
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                gender="Female" if is_female else "Male",
                education_level="Undergraduate",
                degree=random.choice(DEGREES),
                branch=branch,
                college=random.choice(COLLEGES),
                graduation_year=random.choice([2025, 2026, 2027]),
                cgpa=round(random.uniform(5.5, 9.8), 1),
                location=location,
                preferred_locations=preferred_locs,
                preferred_domains=preferred_doms,
                bio=f"Passionate {branch} student interested in {', '.join(preferred_doms[:2])}. "
                    f"Based in {location}. Looking for challenging internship opportunities.",
            )
            db.add(profile)
            db.flush()

            # Add skills based on branch
            branch_skills = _get_branch_skills(branch)
            selected_skills = random.sample(branch_skills, min(random.randint(4, 8), len(branch_skills)))

            for skill_name in selected_skills:
                if skill_name in skill_objects:
                    ss = StudentSkill(
                        student_id=profile.id,
                        skill_id=skill_objects[skill_name].id,
                        proficiency_level=random.choice(["beginner", "intermediate", "advanced", "expert"]),
                    )
                    db.add(ss)

            student_objects.append(profile)

        db.commit()
        print(f"   Created {len(student_objects)} students")

        # 6. Create some applications
        print("📝 Creating applications...")
        app_count = 0
        for student in student_objects[:35]:
            # Each student applies to 1-4 internships
            num_apps = random.randint(1, 4)
            eligible_internships = [i for i in internship_objects if _is_eligible(student, i)]
            if not eligible_internships:
                eligible_internships = internship_objects

            chosen = random.sample(eligible_internships, min(num_apps, len(eligible_internships)))
            for internship in chosen:
                app = Application(
                    student_id=student.id,
                    internship_id=internship.id,
                    status=ApplicationStatus.PENDING,
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                )
                db.add(app)
                app_count += 1

        db.commit()
        print(f"   Created {app_count} applications")

        # 7. Compute match scores
        print("🤖 Computing AI match scores...")
        from app.services.matching_engine import compute_all_matches_for_student
        match_count = 0
        for student in student_objects:
            matches = compute_all_matches_for_student(db, student)
            match_count += len(matches)
        print(f"   Computed {match_count} match scores")

        # 8. Create notifications
        print("🔔 Creating notifications...")
        for student in student_objects[:10]:
            Notification(
                user_id=student.user_id,
                title="Welcome to PM Internship Scheme!",
                message="Complete your profile to get personalized internship recommendations.",
                type=NotificationType.INFO,
            )

        db.commit()

        print("\n✅ Seed completed successfully!")
        print("\n📋 Demo Credentials:")
        print("   Admin:   admin@pmias.gov.in / Admin@123")
        print(f"   Student: {student_objects[0].user.email} / Student@123")
        print(f"   Company: {company_users[0].email} / Company@123")
        print(f"\n📊 Summary:")
        print(f"   Students:     {len(student_objects)}")
        print(f"   Companies:    {len(company_objects)}")
        print(f"   Internships:  {len(internship_objects)}")
        print(f"   Skills:       {len(skill_objects)}")
        print(f"   Applications: {app_count}")
        print(f"   Match Scores: {match_count}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def _get_branch_skills(branch: str) -> list:
    """Get relevant skills for a branch."""
    common = ["Python", "Git", "SQL", "Linux"]
    branch_map = {
        "CSE": common + ["JavaScript", "React", "Node.js", "Machine Learning", "Docker", "AWS", "Data Analysis",
                          "TypeScript", "MongoDB", "PostgreSQL", "Deep Learning", "TensorFlow", "HTML", "CSS",
                          "Java", "C++", "Flask", "FastAPI", "Django"],
        "IT": common + ["JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB", "Docker", "AWS",
                         "TypeScript", "Data Analysis", "Machine Learning", "CI/CD", "Jenkins"],
        "ECE": common + ["C", "C++", "Embedded Systems", "Arduino", "IoT", "MQTT", "Raspberry Pi",
                          "RTOS", "Machine Learning", "Network Security", "MATLAB"],
        "EEE": common + ["C", "C++", "Embedded Systems", "Arduino", "IoT", "RTOS", "MATLAB", "Raspberry Pi"],
        "Mechanical": common + ["C", "C++", "MATLAB", "IoT", "Embedded Systems", "Arduino"],
        "Civil": common + ["MATLAB", "Data Analysis", "AutoCAD"],
    }
    return branch_map.get(branch, common)


def _is_eligible(student: StudentProfile, internship: Internship) -> bool:
    if internship.minimum_cgpa and student.cgpa and student.cgpa < internship.minimum_cgpa:
        return False
    if internship.eligible_branches and student.branch and student.branch not in internship.eligible_branches:
        return False
    return True


if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    seed()
