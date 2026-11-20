import json
from sqlalchemy import Column, Integer, String, Date, Float, Text, DateTime, Boolean, func, Index
from backend.database import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String, index=True, nullable=False)
    company_name = Column(String, index=True, nullable=False)
    company_slug = Column(String, index=True, nullable=False)
    company_logo = Column(String)
    ats_type = Column(String, index=True)

    title = Column(String, index=True, nullable=False)
    normalized_role = Column(String, index=True)
    department = Column(String)

    city = Column(String, index=True)
    state = Column(String)
    country = Column(String, index=True)
    raw_location = Column(String)
    is_remote = Column(Boolean, default=False, index=True)

    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)

    experience_min = Column(Integer, index=True)
    experience_max = Column(Integer, index=True)
    salary_min = Column(Integer)
    salary_max = Column(Integer)

    skills = Column(Text)  # Stored as JSON string
    apply_url = Column(Text, nullable=False)
    description_html = Column(Text)
    description_text = Column(Text)

    posted_date = Column(Date, index=True)
    source = Column(String, default="ats")

    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_job_company_ext", "company_slug", "external_id", unique=True),
        Index("idx_job_filter_bundle", "normalized_role", "country", "is_remote"),
    )

    def to_dict(self):
        skills_list = []
        if self.skills:
            try:
                skills_list = json.loads(self.skills)
            except Exception:
                skills_list = [s.strip() for s in self.skills.split(",") if s.strip()]

        return {
            "job_id": self.job_id,
            "external_id": self.external_id,
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "company_logo": self.company_logo,
            "ats_type": self.ats_type,
            "title": self.title,
            "normalized_role": self.normalized_role,
            "department": self.department,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "raw_location": self.raw_location,
            "is_remote": bool(self.is_remote),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "skills": skills_list,
            "apply_url": self.apply_url,
            "description_text": self.description_text or "",
            "description_html": self.description_html or "",
            "posted_date": str(self.posted_date) if self.posted_date else None,
            "source": self.source,
            "created_at": str(self.created_at) if self.created_at else None,
        }


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    ats_type = Column(String, index=True, nullable=False)  # greenhouse, lever
    region = Column(String, index=True)  # India, Global, Remote
    industry = Column(String)
    website = Column(String)
    logo = Column(String)
    active_jobs = Column(Integer, default=0, index=True)
    status = Column(String, default="active")  # active, syncing, error
    last_synced_at = Column(DateTime)
    error_message = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "ats_type": self.ats_type,
            "region": self.region,
            "industry": self.industry,
            "website": self.website,
            "logo": self.logo,
            "active_jobs": self.active_jobs or 0,
            "status": self.status,
            "last_synced_at": str(self.last_synced_at) if self.last_synced_at else None,
            "error_message": self.error_message,
        }
