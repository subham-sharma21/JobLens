import re
import requests
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Job
import os



def extract_experience(text: str):
    if not text:
        return None, None

    patterns = [
        r"(\d+)\s*-\s*(\d+)\s*years",
        r"(\d+)\+?\s*years",
        r"minimum\s*(\d+)\s*years"
    ]

    text = text.lower()

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                return int(match.group(1)), int(match.group(2))
            else:
                return int(match.group(1)), int(match.group(1)) + 2

    return None, None

# ========= CONFIG =========
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

CITIES = [
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Chennai",
    "Mumbai",
    "Delhi"
]

ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Backend Engineer"
]


def fetch_jobs(role: str, city: str):
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 20,
        "what": role,
        "where": city,
        "content-type": "application/json"
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json().get("results", [])


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "")).date()
    except Exception:
        return None
    

def insert_job(db: Session, job_data: dict, role: str, city: str):
    description = job_data.get("description", "")
    exp_min, exp_max = extract_experience(description)
    job = Job(
        title=job_data.get("title"),
        normalized_role=role,
        company=job_data.get("company", {}).get("display_name"),
        city=city,
        state=None,
        latitude=job_data.get("latitude"),
        longitude=job_data.get("longitude"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        experience_min=exp_min,
        experience_max=exp_max,
        posted_date=parse_date(job_data.get("created")),
        source="adzuna"
    )

    db.add(job)
    try:
        db.commit()
    except Exception:
        db.rollback()  # duplicate or bad data
    finally:
        db.close()


def run():
    for role in ROLES:
        for city in CITIES:
            print(f"Fetching: {role} | {city}")
            jobs = fetch_jobs(role, city)

            for job_data in jobs:
                db = SessionLocal()
                insert_job(db, job_data, role, city)


if __name__ == "__main__":
    run()
