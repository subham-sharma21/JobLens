from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import SessionLocal
from backend.models import Job


from backend.database import engine
from backend.models import Base

Base.metadata.create_all(bind=engine)

#------------ data ingestion endpoint -----------
from backend.ingest_adzuna import ingest_jobs

@app.post("/admin/ingest")
def ingest_data(db: Session = Depends(get_db)):
    ingest_jobs(db)
    return {"status": "ingestion complete"}

# -------------------------------
app = FastAPI(title="Job Market Map API")


# ---------------- DB session dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Health check ----------------
@app.get("/")
def health_check():
    return {"status": "API running"}


# ---------------- Heatmap endpoint ----------------
@app.get("/map/heatmap")
def get_heatmap(
    role: str | None = None,
    exp_min: int | None = None,
    exp_max: int | None = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(
            Job.city,
            Job.latitude,
            Job.longitude,
            func.count(Job.job_id).label("job_count")
        )
        .filter(
            Job.latitude.isnot(None),
            Job.longitude.isnot(None)
        )
        .group_by(
            Job.city,
            Job.latitude,
            Job.longitude
        )
    )

    # ---- Role filter ----
    if role:
        query = query.filter(Job.normalized_role == role)

    # ---- Experience filters ----
    if exp_min is not None:
        query = query.filter(Job.experience_max >= exp_min)

    if exp_max is not None:
        query = query.filter(Job.experience_min <= exp_max)

    results = query.all()

    return [
        {
            "city": r.city,
            "lat": r.latitude,
            "lon": r.longitude,
            "job_count": r.job_count
        }
        for r in results
    ]



