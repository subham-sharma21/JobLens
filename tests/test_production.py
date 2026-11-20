import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.extractor import extract_experience, normalize_role, extract_skills
from backend.services.geocoder import resolve_location


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ==========================================
# 1. NLP EXTRACTOR & GEOCODER UNIT TESTS
# ==========================================
def test_experience_extractor():
    assert extract_experience("Requires 3-5 years of experience in Python") == (3, 5)
    assert extract_experience("Minimum 4 years of software engineering") == (4, 6)
    assert extract_experience("At least 7 yrs working with cloud systems") == (7, 9)
    assert extract_experience("Freshers welcome, 0 to 2 years experience") == (0, 2)
    assert extract_experience("5+ years of distributed systems") == (5, 7)
    assert extract_experience(None) == (None, None)
    assert extract_experience("") == (None, None)
    assert extract_experience("Competitive compensation and 401k") == (None, None)


def test_role_normalizer():
    assert normalize_role("Staff Backend Engineer", "Core Platform") == "Backend Engineer"
    assert normalize_role("Senior React Developer", "Frontend") == "Frontend Engineer"
    assert normalize_role("Lead Data Scientist", "Analytics") == "Data Scientist"
    assert normalize_role("Cloud Infrastructure & DevOps Lead", "Infra") == "DevOps & Cloud Engineer"
    assert normalize_role("Machine Learning Research Scientist", "AI") == "Machine Learning & AI"
    assert normalize_role("VP of People Operations", "HR") == "Other Tech Roles"
    assert normalize_role(None, None) == "Other"


def test_skill_extractor():
    text = "Building scalable microservices with Python, Go, Docker, Kubernetes, and PostgreSQL on AWS."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Go" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills
    assert "AWS" in skills


def test_geocoder():
    # India hub
    geo_blr = resolve_location("Bengaluru, Karnataka, India")
    assert geo_blr["city"] == "Bangalore"
    assert geo_blr["country"] == "India"
    assert geo_blr["latitude"] is not None

    # Global hub
    geo_sf = resolve_location("San Francisco, CA")
    assert geo_sf["city"] == "San Francisco"
    assert geo_sf["country"] == "United States"

    # Remote detection
    geo_rem = resolve_location("Remote - US")
    assert geo_rem["is_remote"] is True

    geo_none = resolve_location(None)
    assert geo_none["is_remote"] is True


# ==========================================
# 2. SYSTEM HEALTH & METRICS TESTS
# ==========================================
def test_health_check(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["total_jobs"] >= 4000
    assert data["companies_tracked"] >= 18


def test_stats_metrics(client):
    res = client.get("/api/v1/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_jobs"] >= 4000
    assert data["total_companies"] >= 18
    assert data["total_cities"] > 50
    assert 0 < data["remote_percentage"] < 100
    assert isinstance(data["top_city"], str)
    assert isinstance(data["top_role"], str)


def test_filters_metadata(client):
    res = client.get("/api/v1/filters")
    assert res.status_code == 200
    data = res.json()
    assert len(data["roles"]) > 5
    assert len(data["companies"]) >= 18
    assert len(data["cities"]) > 20
    assert "India" in data["regions"]
    assert "Global" in data["regions"]


# ==========================================
# 3. JOBS SEARCH & QUERY BUNDLE TESTS
# ==========================================
def test_jobs_pagination(client):
    res1 = client.get("/api/v1/jobs?limit=10&offset=0")
    assert res1.status_code == 200
    data1 = res1.json()
    assert len(data1["jobs"]) == 10

    res2 = client.get("/api/v1/jobs?limit=10&offset=10")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["jobs"]) == 10

    # Ensure different pages return different jobs
    ids1 = {j["job_id"] for j in data1["jobs"]}
    ids2 = {j["job_id"] for j in data2["jobs"]}
    assert ids1.isdisjoint(ids2)


def test_jobs_keyword_search(client):
    res = client.get("/api/v1/jobs?q=python")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    # Every job should match python in title, skills, or description
    for job in data["jobs"][:5]:
        content = f"{job['title']} {job['skills']} {job['description_text']}".lower()
        assert "python" in content


def test_jobs_company_filter(client):
    res = client.get("/api/v1/jobs?company=stripe&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 100
    for job in data["jobs"]:
        assert job["company_slug"] == "stripe"


def test_jobs_remote_filter(client):
    res = client.get("/api/v1/jobs?is_remote=true&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 100
    for job in data["jobs"]:
        assert job["is_remote"] is True


def test_jobs_multi_filter_combination(client):
    res = client.get("/api/v1/jobs?role=Backend%20Engineer&company=stripe&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    for job in data["jobs"]:
        assert job["company_slug"] == "stripe"
        assert job["normalized_role"] == "Backend Engineer"


def test_jobs_no_matches(client):
    res = client.get("/api/v1/jobs?q=superunrealistickeyword999xyz")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert len(data["jobs"]) == 0


def test_job_detail_endpoint(client):
    # Fetch a valid job id first
    list_res = client.get("/api/v1/jobs?limit=1").json()
    valid_id = list_res["jobs"][0]["job_id"]

    res = client.get(f"/api/v1/jobs/{valid_id}")
    assert res.status_code == 200
    job = res.json()
    assert job["job_id"] == valid_id
    assert "apply_url" in job
    assert len(job["apply_url"]) > 5


def test_job_detail_not_found(client):
    res = client.get("/api/v1/jobs/99999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# ==========================================
# 4. GEOSPATIAL MAP ENDPOINT TESTS
# ==========================================
def test_map_clusters(client):
    res = client.get("/api/v1/map")
    assert res.status_code == 200
    clusters = res.json()
    assert isinstance(clusters, list)
    assert len(clusters) > 10

    for c in clusters:
        assert -90 <= c["lat"] <= 90
        assert -180 <= c["lon"] <= 180
        assert c["job_count"] > 0
        assert isinstance(c["city"], str)


def test_map_filtered_by_region(client):
    res = client.get("/api/v1/map?region=India")
    assert res.status_code == 200
    clusters = res.json()
    for c in clusters:
        assert c["country"].lower() == "india" or c["city"].lower() in [
            "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "delhi", "gurgaon", "noida", "chennai"
        ]


# ==========================================
# 5. MARKET ANALYTICS TESTS
# ==========================================
def test_market_analytics(client):
    res = client.get("/api/v1/analytics")
    assert res.status_code == 200
    data = res.json()

    assert len(data["top_companies"]) > 0
    assert len(data["top_roles"]) > 0
    assert len(data["top_hubs"]) > 0
    assert len(data["top_skills"]) > 0

    # Ensure leaderboard counts are descending
    comp_counts = [c["count"] for c in data["top_companies"]]
    assert comp_counts == sorted(comp_counts, reverse=True)


# ==========================================
# 6. COMPANY MANAGEMENT & SYNC TESTS
# ==========================================
def test_companies_directory(client):
    res = client.get("/api/v1/companies")
    assert res.status_code == 200
    companies = res.json()
    assert len(companies) >= 18
    first = companies[0]
    assert "name" in first
    assert "slug" in first
    assert "active_jobs" in first
    assert first["active_jobs"] > 0


def test_add_company_validation(client):
    # Invalid slug with spaces or illegal characters
    res = client.post("/api/v1/companies", json={
        "name": "Invalid Co",
        "slug": "invalid slug with spaces!",
        "ats": "greenhouse"
    })
    assert res.status_code == 422  # Pydantic validation failure

    # Unsupported ATS
    res2 = client.post("/api/v1/companies", json={
        "name": "Invalid ATS Co",
        "slug": "invalidslug",
        "ats": "unsupported_ats"
    })
    assert res2.status_code == 422


def test_add_duplicate_company(client):
    # 'stripe' already exists
    res = client.post("/api/v1/companies", json={
        "name": "Stripe Duplicate",
        "slug": "stripe",
        "ats": "greenhouse"
    })
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()


def test_sync_trigger(client):
    res = client.post("/api/v1/tracker/sync?slug=meesho")
    assert res.status_code == 200
    assert res.json()["status"] in ["accepted", "busy"]
