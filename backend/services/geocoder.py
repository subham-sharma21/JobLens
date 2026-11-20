"""
Geocoding and location normalization service for ATS job postings.
Resolves unstructured location strings into structured cities, countries, and lat/lon coordinates.
"""

from typing import Dict, Any, Tuple, Optional
import re

# Comprehensive coordinates dictionary for major tech hubs (India + Global)
KNOWN_LOCATIONS: Dict[str, Dict[str, Any]] = {
    # --- India Tech Hubs ---
    "bangalore": {"city": "Bangalore", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
    "bengaluru": {"city": "Bangalore", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
    "hyderabad": {"city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867},
    "pune": {"city": "Pune", "state": "Maharashtra", "country": "India", "lat": 18.5204, "lon": 73.8567},
    "mumbai": {"city": "Mumbai", "state": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777},
    "delhi": {"city": "Delhi", "state": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
    "new delhi": {"city": "Delhi", "state": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
    "gurgaon": {"city": "Gurgaon", "state": "Haryana", "country": "India", "lat": 28.4595, "lon": 77.0266},
    "gurugram": {"city": "Gurgaon", "state": "Haryana", "country": "India", "lat": 28.4595, "lon": 77.0266},
    "noida": {"city": "Noida", "state": "Uttar Pradesh", "country": "India", "lat": 28.5355, "lon": 77.3910},
    "chennai": {"city": "Chennai", "state": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707},
    "kolkata": {"city": "Kolkata", "state": "West Bengal", "country": "India", "lat": 22.5726, "lon": 88.3639},
    "ahmedabad": {"city": "Ahmedabad", "state": "Gujarat", "country": "India", "lat": 23.0225, "lon": 72.5714},
    "kochi": {"city": "Kochi", "state": "Kerala", "country": "India", "lat": 9.9312, "lon": 76.2673},

    # --- Global Tech Hubs ---
    "san francisco": {"city": "San Francisco", "state": "CA", "country": "United States", "lat": 37.7749, "lon": -122.4194},
    "new york": {"city": "New York", "state": "NY", "country": "United States", "lat": 40.7128, "lon": -74.0060},
    "seattle": {"city": "Seattle", "state": "WA", "country": "United States", "lat": 47.6062, "lon": -122.3321},
    "austin": {"city": "Austin", "state": "TX", "country": "United States", "lat": 30.2672, "lon": -97.7431},
    "boston": {"city": "Boston", "state": "MA", "country": "United States", "lat": 42.3601, "lon": -71.0589},
    "chicago": {"city": "Chicago", "state": "IL", "country": "United States", "lat": 41.8781, "lon": -87.6298},
    "london": {"city": "London", "state": None, "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278},
    "dublin": {"city": "Dublin", "state": None, "country": "Ireland", "lat": 53.3498, "lon": -6.2603},
    "amsterdam": {"city": "Amsterdam", "state": None, "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
    "berlin": {"city": "Berlin", "state": None, "country": "Germany", "lat": 52.5200, "lon": 13.4050},
    "paris": {"city": "Paris", "state": None, "country": "France", "lat": 48.8566, "lon": 2.3522},
    "singapore": {"city": "Singapore", "state": None, "country": "Singapore", "lat": 1.3521, "lon": 103.8198},
    "toronto": {"city": "Toronto", "state": "ON", "country": "Canada", "lat": 43.6532, "lon": -79.3832},
    "vancouver": {"city": "Vancouver", "state": "BC", "country": "Canada", "lat": 49.2827, "lon": -123.1207},
    "sydney": {"city": "Sydney", "state": "NSW", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
    "tokyo": {"city": "Tokyo", "state": None, "country": "Japan", "lat": 35.6762, "lon": 139.6503},
}

REMOTE_KEYWORDS = ["remote", "virtual", "anywhere", "work from home", "distributed", "telecommute", "home-based"]


def resolve_location(raw_location: Optional[str], default_country: str = "Global") -> Dict[str, Any]:
    """
    Parses any raw location string into structured city, state, country, lat, lon, and remote flag.
    """
    result = {
        "city": "Remote",
        "state": None,
        "country": default_country,
        "latitude": None,
        "longitude": None,
        "is_remote": False,
        "raw_location": raw_location or "Remote"
    }

    if not raw_location:
        result["is_remote"] = True
        return result

    loc_lower = raw_location.lower().strip()

    # Check for remote indicators
    if any(k in loc_lower for k in REMOTE_KEYWORDS):
        result["is_remote"] = True

    # Try matching known tech hubs in the string
    for hub_key, hub_data in KNOWN_LOCATIONS.items():
        # Match as whole word or phrase
        pattern = r"\b" + re.escape(hub_key) + r"\b"
        if re.search(pattern, loc_lower):
            result["city"] = hub_data["city"]
            result["state"] = hub_data["state"]
            result["country"] = hub_data["country"]
            result["latitude"] = hub_data["lat"]
            result["longitude"] = hub_data["lon"]
            return result

    # Check for country mentions
    if "india" in loc_lower:
        result["country"] = "India"
        if result["is_remote"] or "remote" in loc_lower:
            result["city"] = "Remote (India)"
            result["latitude"] = 20.5937
            result["longitude"] = 78.9629
    elif "united states" in loc_lower or " usa" in loc_lower or ", us" in loc_lower:
        result["country"] = "United States"
        if result["is_remote"]:
            result["city"] = "Remote (US)"
            result["latitude"] = 39.8283
            result["longitude"] = -98.5795
    elif "united kingdom" in loc_lower or " uk" in loc_lower:
        result["country"] = "United Kingdom"
        if result["is_remote"]:
            result["city"] = "Remote (UK)"
            result["latitude"] = 55.3781
            result["longitude"] = -3.4360
    elif "canada" in loc_lower:
        result["country"] = "Canada"
        if result["is_remote"]:
            result["city"] = "Remote (Canada)"
            result["latitude"] = 56.1304
            result["longitude"] = -106.3468

    # If city is still remote or unknown, clean up raw name
    if result["city"] == "Remote" and not result["is_remote"]:
        parts = [p.strip() for p in raw_location.split(",") if p.strip()]
        if parts:
            result["city"] = parts[0].title()

    return result
