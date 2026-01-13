from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import SessionLocal
from backend.models import Job

app = FastAPI(title="Job Market Map API")


# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "API running"}


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
        .group_by(Job.city, Job.latitude, Job.longitude)
    )

    if role:
        query = query.filter(Job.normalized_role == role)

    if exp_min is not None:
        query = query.filter(Job.experience_min >= exp_min)

    if exp_max is not None:
        query = query.filter(Job.experience_max <= exp_max)

    results = query.all()

    data = []
    for row in results:
        if row.latitude and row.longitude:
            data.append({
                "city": row.city,
                "lat": row.latitude,
                "lon": row.longitude,
                "job_count": row.job_count
            })

    return data
