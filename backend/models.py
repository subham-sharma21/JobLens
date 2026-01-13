from sqlalchemy import Column, Integer, String, Date, Float, Text, DateTime, func
from backend.database import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    normalized_role = Column(String)
    company = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String, default="India")

    latitude = Column(Float)
    longitude = Column(Float)

    experience_min = Column(Integer)
    experience_max = Column(Integer)

    salary_min = Column(Integer)
    salary_max = Column(Integer)

    posted_date = Column(Date)
    source = Column(String, default="adzuna")

    created_at = Column(
    DateTime,
    server_default=func.now()
    )
