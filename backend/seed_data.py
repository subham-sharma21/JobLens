import random
from datetime import date, timedelta
from backend.database import SessionLocal, init_db
from backend.models import Job

ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Machine Learning Engineer"
]

CITIES_DATA = {
    "Bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "weight": 35},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "weight": 25},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra", "weight": 15},
    "Gurgaon": {"lat": 28.4595, "lon": 77.0266, "state": "Haryana", "weight": 12},
    "Noida": {"lat": 28.5355, "lon": 77.3910, "state": "Uttar Pradesh", "weight": 8},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra", "weight": 15},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu", "weight": 10},
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi", "weight": 10},
}

COMPANIES = [
    "Infosys", "TCS", "Wipro", "Amazon", "Microsoft", "Google", "Flipkart",
    "Swiggy", "Zomato", "PhonePe", "Razorpay", "CRED", "Myntra", "Paytm",
    "Uber", "Oracle", "Goldman Sachs", "Morgan Stanley", "JPMorgan Chase", "Accenture"
]

TITLES = {
    "Data Analyst": ["Senior Data Analyst", "Business Data Analyst", "Product Analyst", "Junior Data Analyst", "Data & BI Analyst"],
    "Data Scientist": ["Lead Data Scientist", "Senior Data Scientist", "NLP Data Scientist", "Computer Vision Specialist", "AI/ML Scientist"],
    "Data Engineer": ["Senior Data Engineer", "Big Data Engineer", "Cloud Data Pipeline Engineer", "ETL Developer", "Snowflake / Spark Engineer"],
    "Backend Engineer": ["Senior Backend Developer (Python/FastAPI)", "Backend Software Engineer (Go/Java)", "Staff Backend Engineer", "Python Backend Developer"],
    "Frontend Engineer": ["Frontend Engineer (React/TypeScript)", "Senior UI Developer", "Frontend Architect", "React/Next.js Engineer"],
    "Full Stack Engineer": ["Full Stack Developer (React + Node)", "Senior Full Stack Engineer (Python/Vue)", "Software Development Engineer II"],
    "DevOps Engineer": ["Cloud DevOps Engineer (AWS/K8s)", "Site Reliability Engineer (SRE)", "Infrastructure & DevOps Lead"],
    "Machine Learning Engineer": ["ML Ops Engineer", "Senior ML Engineer", "Applied AI Engineer", "Deep Learning Research Engineer"]
}


def seed_database(count: int = 150):
    """Populates the database with realistic sample jobs."""
    init_db()
    db = SessionLocal()

    cities = list(CITIES_DATA.keys())
    weights = [CITIES_DATA[c]["weight"] for c in cities]

    added = 0
    today = date.today()

    try:
        for _ in range(count):
            city = random.choices(cities, weights=weights)[0]
            city_meta = CITIES_DATA[city]

            # Add slight jitter to lat/lon so markers don't overlap completely on the map
            lat_jitter = random.uniform(-0.04, 0.04)
            lon_jitter = random.uniform(-0.04, 0.04)

            role = random.choice(ROLES)
            title = random.choice(TITLES[role])
            company = random.choice(COMPANIES)

            exp_min = random.choice([0, 1, 2, 3, 5, 7])
            exp_max = exp_min + random.choice([2, 3, 4])

            # Base salary around Indian Tech salaries (LPA scaled to INR)
            base_lpa = random.randint(6, 40)
            salary_min = base_lpa * 100000
            salary_max = (base_lpa + random.randint(3, 10)) * 100000

            days_ago = random.randint(0, 30)
            posted_date = today - timedelta(days=days_ago)

            job = Job(
                title=title,
                normalized_role=role,
                company=company,
                city=city,
                state=city_meta["state"],
                country="India",
                latitude=city_meta["lat"] + lat_jitter,
                longitude=city_meta["lon"] + lon_jitter,
                experience_min=exp_min,
                experience_max=exp_max,
                salary_min=salary_min,
                salary_max=salary_max,
                posted_date=posted_date,
                source="sample_seed"
            )
            db.add(job)
            added += 1

        db.commit()
        print(f"Successfully seeded {added} sample jobs into the database!")
        return added
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(150)
