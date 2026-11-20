import json
import logging
from typing import Optional, List, Literal
from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI, Depends, Query, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from backend.database import SessionLocal, init_db
from backend.models import Job, Company
from backend.trackers.engine import run_async_engine, load_company_registry, sync_companies_into_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("joblens.api")

# Concurrency lock to prevent overlapping ingestion tasks
_sync_lock = threading.Lock()
_is_syncing = False


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class CompanyCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Company display name")
    slug: str = Field(..., min_length=2, max_length=50, description="ATS board slug identifier")
    ats: Literal["greenhouse", "lever"] = Field(..., description="Supported ATS platform")
    region: str = Field("Global", max_length=50, description="Operating region (India, Global, Remote)")
    industry: Optional[str] = Field("Technology", max_length=100)
    website: Optional[str] = None
    logo: Optional[str] = None

    @field_validator("slug")
    @classmethod
    def clean_slug(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug must contain only alphanumeric characters, dashes, or underscores")
        return cleaned


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        companies = load_company_registry()
        sync_companies_into_db(db, companies)
        logger.info("Database and companies synchronized on startup.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="JobLens — Job Market Intelligence API",
    description="Enterprise REST API for ATS job tracking, geospatial intelligence, and tech labor market analytics.",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for Next.js and frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# HEALTH & METRICS TICKER
# ==========================================
@app.get("/", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    job_count = db.query(func.count(Job.job_id)).scalar() or 0
    company_count = db.query(func.count(Company.id)).scalar() or 0
    return {
        "status": "healthy",
        "service": "JobLens Intelligence API",
        "version": "2.0.0",
        "database": "connected",
        "total_jobs": job_count,
        "companies_tracked": company_count,
        "is_syncing": _is_syncing,
        "docs": "/docs"
    }


@app.get("/api/v1/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    total_jobs = db.query(func.count(Job.job_id)).scalar() or 0
    total_companies = db.query(func.count(Company.id)).scalar() or 0
    total_cities = db.query(func.count(func.distinct(Job.city))).filter(Job.city != "Remote").scalar() or 0

    remote_count = db.query(func.count(Job.job_id)).filter(Job.is_remote == True).scalar() or 0
    remote_pct = round((remote_count / total_jobs * 100), 1) if total_jobs > 0 else 0

    top_city_row = (
        db.query(Job.city, func.count(Job.job_id).label("c"))
        .filter(Job.city != "Remote", Job.city.isnot(None))
        .group_by(Job.city)
        .order_by(desc("c"))
        .first()
    )
    top_city = top_city_row[0] if top_city_row else "Bangalore"

    top_role_row = (
        db.query(Job.normalized_role, func.count(Job.job_id).label("c"))
        .filter(Job.normalized_role.isnot(None))
        .group_by(Job.normalized_role)
        .order_by(desc("c"))
        .first()
    )
    top_role = top_role_row[0] if top_role_row else "Software Engineer"

    return {
        "total_jobs": total_jobs,
        "total_companies": total_companies,
        "total_cities": total_cities,
        "remote_count": remote_count,
        "remote_percentage": remote_pct,
        "top_city": top_city,
        "top_role": top_role,
        "is_syncing": _is_syncing,
    }


# ==========================================
# FILTER METADATA
# ==========================================
@app.get("/api/v1/filters", tags=["Metadata"])
def get_filter_options(db: Session = Depends(get_db)):
    roles = [
        r[0] for r in db.query(Job.normalized_role)
        .filter(Job.normalized_role.isnot(None))
        .distinct()
        .order_by(Job.normalized_role.asc())
        .all() if r[0]
    ]

    companies = [
        {"name": c.name, "slug": c.slug, "region": c.region, "logo": c.logo}
        for c in db.query(Company).order_by(Company.name.asc()).all()
    ]

    cities = [
        r[0] for r in db.query(Job.city)
        .filter(Job.city.isnot(None), Job.city != "Remote")
        .distinct()
        .order_by(Job.city.asc())
        .all() if r[0]
    ]

    return {
        "roles": roles,
        "companies": companies,
        "cities": cities,
        "regions": ["All", "India", "Global", "Remote"]
    }


# ==========================================
# JOB LISTINGS & SEARCH
# ==========================================
def apply_job_filters(query, q, role, company, city, country, is_remote, exp_min, exp_max, region):
    if q and q.strip():
        search_pattern = f"%{q.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Job.title).like(search_pattern),
                func.lower(Job.company_name).like(search_pattern),
                func.lower(Job.skills).like(search_pattern),
                func.lower(Job.description_text).like(search_pattern),
            )
        )

    if role and role.lower() != "all":
        query = query.filter(func.lower(Job.normalized_role) == role.lower())

    if company and company.lower() != "all":
        query = query.filter(func.lower(Job.company_slug) == company.lower())

    if city and city.lower() != "all":
        query = query.filter(func.lower(Job.city) == city.lower())

    if country and country.lower() != "all":
        query = query.filter(func.lower(Job.country) == country.lower())

    if is_remote is not None:
        query = query.filter(Job.is_remote == is_remote)

    if exp_min is not None:
        query = query.filter(Job.experience_max >= exp_min)

    if exp_max is not None:
        query = query.filter(Job.experience_min <= exp_max)

    if region and region.lower() != "all":
        if region.lower() == "india":
            query = query.filter(
                or_(
                    func.lower(Job.country) == "india",
                    func.lower(Job.city).in_(["bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "delhi", "gurgaon", "gurugram", "noida", "chennai"])
                )
            )
        elif region.lower() == "remote":
            query = query.filter(Job.is_remote == True)

    return query


@app.get("/api/v1/jobs", tags=["Jobs"])
def list_jobs(
    q: Optional[str] = Query(None, description="Search keyword"),
    role: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    exp_min: Optional[int] = Query(None),
    exp_max: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    query = apply_job_filters(query, q, role, company, city, country, is_remote, exp_min, exp_max, region)

    total = query.count()
    jobs = query.order_by(desc(Job.created_at), desc(Job.job_id)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "jobs": [j.to_dict() for j in jobs]
    }


@app.get("/api/v1/jobs/{job_id}", tags=["Jobs"])
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting with ID {job_id} not found"
        )
    return job.to_dict()


# ==========================================
# GEOSPATIAL MAP DATA
# ==========================================
@app.get("/api/v1/map", tags=["Maps"])
def get_map_points(
    q: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    exp_min: Optional[int] = Query(None),
    exp_max: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = (
        db.query(
            Job.city,
            Job.country,
            Job.latitude,
            Job.longitude,
            Job.is_remote,
            func.count(Job.job_id).label("job_count")
        )
        .filter(
            Job.latitude.isnot(None),
            Job.longitude.isnot(None)
        )
    )

    query = apply_job_filters(query, q, role, company, city, country, is_remote, exp_min, exp_max, region)

    results = (
        query.group_by(
            Job.city,
            Job.country,
            Job.latitude,
            Job.longitude,
            Job.is_remote
        )
        .order_by(desc("job_count"))
        .all()
    )

    return [
        {
            "city": r.city,
            "country": r.country,
            "lat": r.latitude,
            "lon": r.longitude,
            "is_remote": r.is_remote,
            "job_count": r.job_count
        }
        for r in results
    ]


# Backward compatibility for legacy heatmap
@app.get("/map/heatmap", tags=["Maps"])
def get_legacy_heatmap(
    role: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    exp_min: Optional[int] = Query(None),
    exp_max: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    return get_map_points(role=role, city=city, exp_min=exp_min, exp_max=exp_max, db=db)


# ==========================================
# MARKET INTELLIGENCE & ANALYTICS
# ==========================================
@app.get("/api/v1/analytics", tags=["Analytics"])
def get_analytics(db: Session = Depends(get_db)):
    top_companies = (
        db.query(
            Job.company_name,
            Job.company_slug,
            func.count(Job.job_id).label("job_count")
        )
        .group_by(Job.company_name, Job.company_slug)
        .order_by(desc("job_count"))
        .limit(10)
        .all()
    )

    top_roles = (
        db.query(
            Job.normalized_role,
            func.count(Job.job_id).label("job_count")
        )
        .filter(Job.normalized_role.isnot(None))
        .group_by(Job.normalized_role)
        .order_by(desc("job_count"))
        .limit(10)
        .all()
    )

    top_hubs = (
        db.query(
            Job.city,
            Job.country,
            func.count(Job.job_id).label("job_count")
        )
        .filter(Job.city.isnot(None), Job.city != "Remote")
        .group_by(Job.city, Job.country)
        .order_by(desc("job_count"))
        .limit(10)
        .all()
    )

    skill_counts = {}
    jobs_with_skills = db.query(Job.skills).filter(Job.skills.isnot(None)).limit(1000).all()
    for row in jobs_with_skills:
        try:
            skills = json.loads(row[0]) if row[0] else []
            for s in skills:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        except Exception:
            pass

    top_skills = sorted(
        [{"skill": k, "count": v} for k, v in skill_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:15]

    return {
        "top_companies": [{"name": r.company_name, "slug": r.company_slug, "count": r.job_count} for r in top_companies],
        "top_roles": [{"role": r.normalized_role, "count": r.job_count} for r in top_roles],
        "top_hubs": [{"city": r.city, "country": r.country, "count": r.job_count} for r in top_hubs],
        "top_skills": top_skills,
    }


# ==========================================
# TRACKED COMPANIES & SYNC MANAGEMENT
# ==========================================
@app.get("/api/v1/companies", tags=["Companies"])
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).order_by(desc(Company.active_jobs)).all()
    return [c.to_dict() for c in companies]


@app.post("/api/v1/companies", tags=["Companies"])
def add_company(payload: CompanyCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.slug == payload.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with slug '{payload.slug}' is already registered."
        )

    new_comp = Company(
        name=payload.name,
        slug=payload.slug,
        ats_type=payload.ats,
        region=payload.region,
        industry=payload.industry,
        website=payload.website or f"https://{payload.slug}.com",
        logo=payload.logo or f"https://{payload.slug}.com/favicon.ico",
        status="active"
    )
    db.add(new_comp)
    db.commit()
    db.refresh(new_comp)

    return {
        "status": "success",
        "message": f"Successfully registered {payload.name} ({payload.ats.upper()})",
        "company": new_comp.to_dict()
    }


@app.post("/api/v1/tracker/sync", tags=["Tracker"])
def trigger_sync(background_tasks: BackgroundTasks, slug: Optional[str] = Query(None)):
    """Triggers background resync of ATS job boards with concurrency lock."""
    global _is_syncing

    with _sync_lock:
        if _is_syncing:
            return {
                "status": "busy",
                "message": "A synchronization process is already actively running. Please wait for it to complete."
            }
        _is_syncing = True

    def run_sync_task():
        global _is_syncing
        import asyncio
        try:
            if slug:
                companies = [c for c in load_company_registry() if c.get("slug") == slug]
            else:
                companies = load_company_registry()
            asyncio.run(run_async_engine(companies=companies))
        except Exception as err:
            logger.error("Background sync error: %s", str(err))
        finally:
            with _sync_lock:
                _is_syncing = False

    background_tasks.add_task(run_sync_task)
    target = f"company '{slug}'" if slug else "all companies"
    return {"status": "accepted", "message": f"Sync queued in background for {target}"}
