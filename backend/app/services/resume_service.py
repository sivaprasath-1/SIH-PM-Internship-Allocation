"""
Resume Analysis Service
Extracts skills, education, and other data from PDF resumes.
"""
import re
from typing import Dict, List, Optional


# Comprehensive skill dictionary for matching
SKILL_DICTIONARY = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell",
        "Bash", "PowerShell", "Dart", "Lua", "Haskell", "Elixir",
    ],
    "Web Development": [
        "HTML", "CSS", "React", "Angular", "Vue", "Next.js", "Node.js", "Express",
        "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", "Laravel", "Rails",
        "Svelte", "jQuery", "Bootstrap", "Tailwind CSS", "SASS", "LESS",
        "REST API", "GraphQL", "WebSocket",
    ],
    "Data Science & AI/ML": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
        "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV", "NLTK", "SpaCy",
        "Hugging Face", "GPT", "LLM", "Neural Networks", "CNN", "RNN", "LSTM",
        "Random Forest", "SVM", "XGBoost", "Data Analysis", "Data Visualization",
        "Statistics", "Linear Regression", "Logistic Regression",
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "CI/CD", "GitHub Actions", "GitLab CI", "Ansible", "Puppet",
        "Chef", "Nginx", "Apache", "Linux", "Ubuntu", "CentOS",
    ],
    "Database": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "Firebase", "SQLite", "Oracle", "SQL Server",
        "Neo4j", "InfluxDB",
    ],
    "Cybersecurity": [
        "Cybersecurity", "Penetration Testing", "Ethical Hacking", "Network Security",
        "Cryptography", "OWASP", "Firewall", "IDS", "IPS", "SIEM", "SOC",
        "Vulnerability Assessment", "Malware Analysis", "Digital Forensics",
    ],
    "Embedded & IoT": [
        "Embedded Systems", "IoT", "Arduino", "Raspberry Pi", "RTOS", "FPGA",
        "Verilog", "VHDL", "Microcontroller", "ARM", "ESP32", "Sensor",
        "MQTT", "Zigbee", "LoRa",
    ],
    "Tools & Others": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
        "Figma", "Adobe XD", "Photoshop", "Illustrator", "Postman",
        "Swagger", "VS Code", "IntelliJ", "Eclipse", "Jupyter",
        "Agile", "Scrum", "Kanban", "DevOps", "Blockchain", "Ethereum",
        "Solidity", "Power BI", "Tableau", "Excel", "SAP",
    ],
}

# Flatten for quick lookup
ALL_SKILLS = {}
for category, skills in SKILL_DICTIONARY.items():
    for skill in skills:
        ALL_SKILLS[skill.lower()] = {"name": skill, "category": category}


def extract_resume_data(filepath: str) -> Dict:
    """Extract structured data from a PDF resume."""
    text = _extract_text_from_pdf(filepath)
    if not text:
        return {
            "name": None,
            "education": None,
            "degree": None,
            "branch": None,
            "skills": [],
            "projects": [],
            "experience": [],
            "certifications": [],
        }

    return {
        "name": _extract_name(text),
        "education": _extract_education(text),
        "degree": _extract_degree(text),
        "branch": _extract_branch(text),
        "skills": _extract_skills(text),
        "projects": _extract_projects(text),
        "experience": _extract_experience(text),
        "certifications": _extract_certifications(text),
    }


def _extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        # Fallback: try PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception:
            return ""
    except Exception:
        return ""


def _extract_name(text: str) -> Optional[str]:
    """Try to extract name from first lines of resume."""
    lines = text.strip().split("\n")
    for line in lines[:3]:
        line = line.strip()
        if line and len(line) < 50 and not any(c.isdigit() for c in line):
            # Likely a name
            if "@" not in line and "http" not in line.lower():
                return line
    return None


def _extract_education(text: str) -> Optional[str]:
    """Extract education information."""
    education_patterns = [
        r"(?i)(B\.?Tech|B\.?E\.?|M\.?Tech|M\.?E\.?|B\.?Sc|M\.?Sc|B\.?CA|M\.?CA|BBA|MBA|Ph\.?D)",
        r"(?i)(Bachelor|Master|Doctorate)",
        r"(?i)(Engineering|Technology|Science|Computer|Information)",
    ]
    for pattern in education_patterns:
        match = re.search(pattern, text)
        if match:
            # Get surrounding context
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 100)
            return text[start:end].strip()
    return None


def _extract_degree(text: str) -> Optional[str]:
    degree_map = {
        r"(?i)\bB\.?Tech\b": "B.Tech",
        r"(?i)\bB\.?E\.?\b": "B.E.",
        r"(?i)\bM\.?Tech\b": "M.Tech",
        r"(?i)\bM\.?E\.?\b": "M.E.",
        r"(?i)\bB\.?Sc\b": "B.Sc",
        r"(?i)\bM\.?Sc\b": "M.Sc",
        r"(?i)\bB\.?CA\b": "BCA",
        r"(?i)\bM\.?CA\b": "MCA",
        r"(?i)\bMBA\b": "MBA",
        r"(?i)\bPh\.?D\b": "Ph.D",
    }
    for pattern, degree in degree_map.items():
        if re.search(pattern, text):
            return degree
    return None


def _extract_branch(text: str) -> Optional[str]:
    branches = {
        r"(?i)\b(computer\s*science|CSE|CS)\b": "CSE",
        r"(?i)\b(information\s*technology|IT)\b": "IT",
        r"(?i)\b(electronics?\s*(and|&)\s*communication|ECE)\b": "ECE",
        r"(?i)\b(electrical|EEE)\b": "EEE",
        r"(?i)\b(mechanical|ME)\b": "Mechanical",
        r"(?i)\b(civil)\b": "Civil",
        r"(?i)\b(chemical)\b": "Chemical",
        r"(?i)\b(aerospace)\b": "Aerospace",
        r"(?i)\b(biotech|biotechnology)\b": "Biotechnology",
    }
    for pattern, branch in branches.items():
        if re.search(pattern, text):
            return branch
    return None


def _extract_skills(text: str) -> List[str]:
    """Extract skills using dictionary matching."""
    found_skills = set()
    text_lower = text.lower()

    for skill_lower, skill_info in ALL_SKILLS.items():
        # Use word boundary matching for short skills
        if len(skill_lower) <= 3:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill_info["name"])
        else:
            if skill_lower in text_lower:
                found_skills.add(skill_info["name"])

    return sorted(list(found_skills))


def _extract_projects(text: str) -> List[str]:
    """Extract project titles."""
    projects = []
    lines = text.split("\n")
    in_projects = False
    for line in lines:
        line = line.strip()
        if re.search(r"(?i)^projects?", line):
            in_projects = True
            continue
        if in_projects:
            if re.search(r"(?i)^(experience|education|skills|certif)", line):
                break
            if line and len(line) > 5 and len(line) < 200:
                # Clean bullet points
                line = re.sub(r'^[\-•\*\d\.]+\s*', '', line)
                if line:
                    projects.append(line)
    return projects[:10]


def _extract_experience(text: str) -> List[str]:
    """Extract experience entries."""
    experiences = []
    lines = text.split("\n")
    in_experience = False
    for line in lines:
        line = line.strip()
        if re.search(r"(?i)^(experience|work\s*experience|internship)", line):
            in_experience = True
            continue
        if in_experience:
            if re.search(r"(?i)^(education|skills|projects|certif)", line):
                break
            if line and len(line) > 5 and len(line) < 200:
                line = re.sub(r'^[\-•\*\d\.]+\s*', '', line)
                if line:
                    experiences.append(line)
    return experiences[:10]


def _extract_certifications(text: str) -> List[str]:
    """Extract certifications."""
    certs = []
    lines = text.split("\n")
    in_certs = False
    for line in lines:
        line = line.strip()
        if re.search(r"(?i)^(certif|certification|licenses?)", line):
            in_certs = True
            continue
        if in_certs:
            if re.search(r"(?i)^(education|skills|projects|experience)", line):
                break
            if line and len(line) > 5 and len(line) < 200:
                line = re.sub(r'^[\-•\*\d\.]+\s*', '', line)
                if line:
                    certs.append(line)
    return certs[:10]
