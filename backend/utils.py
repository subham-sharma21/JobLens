"""
JobLens utility functions for data processing, formatting, and geo-normalization.
"""

from typing import Optional, Tuple

CITY_COORDINATES = {
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "chennai": (13.0827, 80.2707),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "noida": (28.5355, 77.3910),
    "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
}


def get_city_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """Returns (latitude, longitude) for known cities, or None if unknown."""
    if not city_name:
        return None
    return CITY_COORDINATES.get(city_name.strip().lower())


def format_salary_lpa(amount_inr: Optional[int]) -> str:
    """Formats an annual INR salary into Lakhs per Annum (LPA) string."""
    if amount_inr is None or amount_inr <= 0:
        return "Not Disclosed"
    lpa = amount_inr / 100000
    if lpa.is_integer():
        return f"₹{int(lpa)} LPA"
    return f"₹{lpa:.1f} LPA"


def normalize_role_title(raw_title: str) -> str:
    """Normalizes job titles into standard category names."""
    if not raw_title:
        return "Other"

    title_lower = raw_title.lower()

    if "analyst" in title_lower or "analytics" in title_lower:
        return "Data Analyst"
    if "scientist" in title_lower:
        return "Data Scientist"
    if "data engineer" in title_lower or "etl" in title_lower or "big data" in title_lower:
        return "Data Engineer"
    if "backend" in title_lower:
        return "Backend Engineer"
    if "frontend" in title_lower or "react" in title_lower or "angular" in title_lower or "ui" in title_lower:
        return "Frontend Engineer"
    if "full stack" in title_lower or "fullstack" in title_lower:
        return "Full Stack Engineer"
    if "devops" in title_lower or "sre" in title_lower or "cloud" in title_lower:
        return "DevOps Engineer"
    if "machine learning" in title_lower or "ml" in title_lower or "ai" in title_lower:
        return "Machine Learning Engineer"

    return raw_title.strip().title()
