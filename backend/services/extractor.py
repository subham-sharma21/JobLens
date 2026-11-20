"""
NLP and heuristic feature extraction for job descriptions.
Extracts experience ranges, normalized role classifications, and technical skills.
"""

import re
from typing import Tuple, Optional, List
from html import unescape

TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Go", "Golang", "Java", "C++", "C#", "Rust", "Ruby",
    "React", "Next.js", "Vue", "Angular", "Node.js", "FastAPI", "Django", "Flask", "GraphQL", "REST",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "Linux", "Kafka",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Snowflake", "Spark",
    "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "NLP", "LLM", "GenAI", "Scikit-Learn",
    "Git", "Microservices", "System Design", "Distributed Systems"
]


def clean_html(raw_html: Optional[str]) -> str:
    """Removes HTML tags and decodes HTML entities into clean readable text."""
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = unescape(clean)
    return " ".join(clean.split())


def extract_experience(text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Extracts minimum and maximum years of experience from job descriptions."""
    if not text:
        return None, None

    patterns = [
        r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs)",
        r"(\d+)\+?\s*(?:years|yrs)",
        r"(?:minimum|at least)\s*(\d+)\s*(?:years|yrs)",
        r"experience[:\s]+(\d+)\s*(?:-|to)\s*(\d+)"
    ]

    clean_text = text.lower()

    for pattern in patterns:
        match = re.search(pattern, clean_text)
        if match:
            groups = match.groups()
            if len(groups) == 2 and groups[1] is not None:
                return int(groups[0]), int(groups[1])
            elif len(groups) >= 1 and groups[0] is not None:
                min_exp = int(groups[0])
                return min_exp, min_exp + 2

    return None, None


def normalize_role(title: Optional[str], department: Optional[str] = "") -> str:
    """Classifies a job into standard technical domain categories."""
    if not title:
        return "Other"

    t = title.lower()
    d = (department or "").lower()

    if "machine learning" in t or "ml" in t or "ai" in t or "deep learning" in t or "nlp" in t or "computer vision" in t:
        return "Machine Learning & AI"
    if "data scientist" in t or "scientist" in t:
        return "Data Scientist"
    if "data engineer" in t or "big data" in t or "etl" in t or "analytics engineer" in t:
        return "Data Engineer"
    if "data analyst" in t or "business analyst" in t or "bi analyst" in t:
        return "Data Analyst"
    if "backend" in t or "back-end" in t or "back end" in t or "python developer" in t or "golang" in t or "java developer" in t:
        return "Backend Engineer"
    if "frontend" in t or "front-end" in t or "ui engineer" in t or "react" in t:
        return "Frontend Engineer"
    if "full stack" in t or "fullstack" in t or "full-stack" in t:
        return "Full Stack Engineer"
    if "devops" in t or "sre" in t or "reliability" in t or "infrastructure" in t or "cloud engineer" in t or "platform engineer" in t:
        return "DevOps & Cloud Engineer"
    if "security" in t or "cyber" in t or "infosec" in t:
        return "Security Engineer"
    if "mobile" in t or "ios" in t or "android" in t or "flutter" in t or "react native" in t:
        return "Mobile Engineer"
    if "product manager" in t or "product owner" in t:
        return "Product Management"
    if "design" in t or "ui/ux" in t or "product designer" in t:
        return "Product Design"
    if "qa" in t or "quality" in t or "test" in t or "sdet" in t:
        return "QA & Test Engineering"
    if "engineering" in d or "software" in t or "developer" in t or "architect" in t:
        return "Software Engineer"

    return "Other Tech Roles"


def extract_skills(text: Optional[str]) -> List[str]:
    """Identifies technical skills mentioned in the job title or description."""
    if not text:
        return []

    found = set()
    text_clean = f" {text} "

    for skill in TECH_SKILLS:
        # Match as whole word with word boundaries
        pattern = r"(?i)\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_clean):
            found.add(skill)

    return sorted(list(found))
