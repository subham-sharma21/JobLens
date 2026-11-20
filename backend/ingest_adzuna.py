import os
import re
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.database import SessionLocal, init_db
from backend.models import Job

load_dotenv()
logger = logging.getLogger("joblens.ingest")

# ========= CONFIG =========
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

DEFAULT_CITIES = [
    "Bangalore",
    "Hyderabad",
    "Pune",
    "Chennai",
    "Mumbai",
    "Delhi",
    "Gurgaon",
    "Noida"
]

DEFAULT_ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer"
]

CITY_COORDINATES = {
    "Bangalore": (12.9716, 77.5946),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Chennai": (13.0827, 80.2707),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "New Delhi": (28.6139, 77.2090),
    "Noida": (28.5355, 77.3910),
    "Gurgaon": (28.4595, 77.0266),
    "Gurugram": (28.4595, 77.0266),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
}


def extract_experience(text: str):
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


def parse_date(date_str):
    """Parses ISO timestamp from Adzuna API into Python date."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "")).date()
    except Exception:
        return None


def fetch_jobs(role: str, city: str, results_per_page: int = 20):
    """Fetches job listings from Adzuna API."""
    if not APP_ID or not APP_KEY:
        raise ValueError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in the environment or .env")

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": role,
        "where": city,
        "content-type": "application/json"
    }

    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json().get("results", [])


def insert_job(db: Session, job_data: dict, role: str, city: str):
    """Inserts a single job record into the database."""
    description = job_data.get("description", "")
    exp_min, exp_max = extract_experience(description)

    # Use coordinates from API or fallback to city dictionary
    lat = job_data.get("latitude")
    lon = job_data.get("longitude")

    if (lat is None or lon is None) and city in CITY_COORDINATES:
        lat, lon = CITY_COORDINATES[city]

    company_info = job_data.get("company", {})
    company_name = company_info.get("display_name") if isinstance(company_info, dict) else str(company_info)

    job = Job(
        title=job_data.get("title", f"{role} position"),
        normalized_role=role,
        company=company_name or "Confidential",
        city=city,
        state=None,
        latitude=lat,
        longitude=lon,
        salary_min=int(job_data.get("salary_min")) if job_data.get("salary_min") else None,
        salary_max=int(job_data.get("salary_max")) if job_data.get("salary_max") else None,
        experience_min=exp_min,
        experience_max=exp_max,
        posted_date=parse_date(job_data.get("created")),
        source="adzuna"
    )

    db.add(job)
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.warning("Could not insert job '%s': %s", job.title, str(e))
        return False


def ingest_jobs(db: Session = None, roles: list = None, cities: list = None, results_per_page: int = 15):
    """
    Main ingestion coordinator. Can be called with an existing session (FastAPI)
    or will manage its own session when run as a standalone script.
    """
    init_db()

    target_roles = roles or DEFAULT_ROLES
    target_cities = cities or DEFAULT_CITIES

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    stats = {
        "roles_processed": len(target_roles),
        "cities_processed": len(target_cities),
        "total_fetched": 0,
        "total_inserted": 0,
        "errors": []
    }

    try:
        for role in target_roles:
            for city in target_cities:
                try:
                    jobs = fetch_jobs(role, city, results_per_page=results_per_page)
                    stats["total_fetched"] += len(jobs)
                    for job_data in jobs:
                        if insert_job(db, job_data, role, city):
                            stats["total_inserted"] += 1
                except Exception as ex:
                    stats["errors"].append(f"{role} @ {city}: {str(ex)}")
                    logger.error("Failed fetching %s in %s: %s", role, city, str(ex))
    finally:
        if should_close:
            db.close()

    return stats


def run():
    print("Starting Adzuna Ingestion...")
    stats = ingest_jobs()
    print(f"Ingestion finished: {stats['total_inserted']} jobs inserted from {stats['total_fetched']} fetched.")
    if stats["errors"]:
        print(f"Encountered {len(stats['errors'])} errors (check API keys or network).")


if __name__ == "__main__":
    run()
