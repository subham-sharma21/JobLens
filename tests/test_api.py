import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["total_jobs"] > 0


def test_stats_endpoint(client):
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "total_companies" in data
    assert "remote_percentage" in data


def test_filters_endpoint(client):
    response = client.get("/api/v1/filters")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert "companies" in data
    assert len(data["companies"]) > 0


def test_jobs_search(client):
    response = client.get("/api/v1/jobs?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["jobs"]) == 5
    first = data["jobs"][0]
    assert "title" in first
    assert "company_name" in first
    assert "apply_url" in first


def test_map_data(client):
    response = client.get("/api/v1/map")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "lat" in data[0]
    assert "lon" in data[0]
    assert "job_count" in data[0]


def test_analytics(client):
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "top_companies" in data
    assert "top_roles" in data
    assert "top_skills" in data


def test_companies_list(client):
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "active_jobs" in data[0]
