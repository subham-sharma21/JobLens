"""
Async ATS Ingestion Engine.
Coordinates parallel fetching, geocoding, skill extraction, and database persistence.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional

import httpx
from sqlalchemy.orm import Session

from backend.database import SessionLocal, init_db
from backend.models import Job, Company
from backend.trackers.greenhouse import GreenhouseTracker
from backend.trackers.lever import LeverTracker
from backend.services.geocoder import resolve_location
from backend.services.extractor import normalize_role, extract_experience, extract_skills

logger = logging.getLogger("joblens.engine")
logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPANIES_FILE = os.path.join(PROJECT_ROOT, "data", "companies.json")


def load_company_registry() -> List[Dict[str, Any]]:
    """Loads company list from data/companies.json."""
    if os.path.exists(COMPANIES_FILE):
        with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def sync_companies_into_db(db: Session, companies: List[Dict[str, Any]]):
    """Ensures all registry companies exist in the companies database table."""
    for c in companies:
        slug = c.get("slug")
        existing = db.query(Company).filter(Company.slug == slug).first()
        if not existing:
            comp = Company(
                name=c.get("name"),
                slug=slug,
                ats_type=c.get("ats"),
                region=c.get("region"),
                industry=c.get("industry"),
                website=c.get("website"),
                logo=c.get("logo"),
                status="active"
            )
            db.add(comp)
    db.commit()


async def fetch_company_jobs(
    client: httpx.AsyncClient,
    company: Dict[str, Any],
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """Fetches jobs for a single company respecting concurrency limits."""
    ats = company.get("ats", "").lower()
    async with semaphore:
        if ats == "greenhouse":
            tracker = GreenhouseTracker()
        elif ats == "lever":
            tracker = LeverTracker()
        else:
            return {"company": company, "jobs": [], "error": f"Unsupported ATS: {ats}"}

        jobs = await tracker.fetch_jobs(client, company)
        return {"company": company, "jobs": jobs, "error": None}


def persist_jobs(db: Session, company_meta: Dict[str, Any], raw_jobs: List[Dict[str, Any]]) -> int:
    """Normalizes and saves fetched jobs into the database."""
    slug = company_meta.get("slug")
    today = date.today()
    inserted_or_updated = 0

    for item in raw_jobs:
        ext_id = item["external_id"]
        title = item["title"]
        desc_text = item.get("description_text", "")
        desc_html = item.get("description_html", "")

        # Geocode and extract features
        geo = resolve_location(item.get("raw_location"), default_country=company_meta.get("region", "Global"))
        role = normalize_role(title, item.get("department"))
        exp_min, exp_max = extract_experience(desc_text)
        skills = extract_skills(f"{title} {desc_text}")

        # Check existing job record
        existing = db.query(Job).filter(Job.company_slug == slug, Job.external_id == ext_id).first()

        if existing:
            existing.title = title
            existing.normalized_role = role
            existing.department = item.get("department")
            existing.city = geo["city"]
            existing.state = geo["state"]
            existing.country = geo["country"]
            existing.raw_location = geo["raw_location"]
            existing.is_remote = geo["is_remote"]
            existing.latitude = geo["latitude"]
            existing.longitude = geo["longitude"]
            existing.experience_min = exp_min
            existing.experience_max = exp_max
            existing.skills = json.dumps(skills)
            existing.apply_url = item.get("apply_url")
            existing.description_text = desc_text
            existing.description_html = desc_html
        else:
            new_job = Job(
                external_id=ext_id,
                company_name=company_meta.get("name"),
                company_slug=slug,
                company_logo=company_meta.get("logo"),
                ats_type=company_meta.get("ats"),
                title=title,
                normalized_role=role,
                department=item.get("department"),
                city=geo["city"],
                state=geo["state"],
                country=geo["country"],
                raw_location=geo["raw_location"],
                is_remote=geo["is_remote"],
                latitude=geo["latitude"],
                longitude=geo["longitude"],
                experience_min=exp_min,
                experience_max=exp_max,
                skills=json.dumps(skills),
                apply_url=item.get("apply_url"),
                description_text=desc_text,
                description_html=desc_html,
                posted_date=today,
                source=company_meta.get("ats")
            )
            db.add(new_job)

        inserted_or_updated += 1

    # Update company record
    comp_record = db.query(Company).filter(Company.slug == slug).first()
    if comp_record:
        comp_record.active_jobs = len(raw_jobs)
        comp_record.last_synced_at = datetime.now()
        comp_record.status = "active"

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed persisting jobs for %s: %s", slug, str(e))

    return inserted_or_updated


async def run_async_engine(
    companies: Optional[List[Dict[str, Any]]] = None,
    concurrency: int = 8
) -> Dict[str, Any]:
    """Runs the asynchronous ingestion pipeline across all companies."""
    init_db()
    db = SessionLocal()

    if not companies:
        companies = load_company_registry()

    sync_companies_into_db(db, companies)

    semaphore = asyncio.Semaphore(concurrency)
    headers = {
        "User-Agent": "JobLens-Market-Intelligence/2.0 (Career Discovery Platform)"
    }

    stats = {
        "companies_total": len(companies),
        "companies_synced": 0,
        "total_jobs_ingested": 0,
        "errors": []
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        tasks = [fetch_company_jobs(client, c, semaphore) for c in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                stats["errors"].append(str(res))
                continue

            company = res["company"]
            jobs = res["jobs"]
            err = res["error"]

            if err:
                stats["errors"].append(f"{company.get('name')}: {err}")
                continue

            count = persist_jobs(db, company, jobs)
            stats["total_jobs_ingested"] += count
            stats["companies_synced"] += 1
            logger.info("Synced %s: %d active jobs", company.get("name"), len(jobs))

    db.close()
    return stats


def run():
    print("=" * 60)
    print("🚀 Starting JobLens ATS Multi-Company Ingestion Engine...")
    print("=" * 60)
    result = asyncio.run(run_async_engine())
    print("\n" + "=" * 60)
    print(f"✅ Ingestion Complete!")
    print(f"📊 Companies Synced: {result['companies_synced']}/{result['companies_total']}")
    print(f"💼 Total Jobs Ingested: {result['total_jobs_ingested']}")
    if result["errors"]:
        print(f"⚠️ Warnings/Errors: {len(result['errors'])}")
    print("=" * 60)


if __name__ == "__main__":
    run()
