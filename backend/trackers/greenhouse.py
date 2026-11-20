"""
Greenhouse ATS API Tracker.
Queries: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
"""

from typing import Dict, Any, List
from html import unescape
import httpx
import logging
from backend.trackers.base import BaseTracker
from backend.services.extractor import clean_html

logger = logging.getLogger("joblens.trackers.greenhouse")


class GreenhouseTracker(BaseTracker):
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"

    async def fetch_jobs(self, client: httpx.AsyncClient, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        slug = company.get("slug")
        url = self.BASE_URL.format(slug=slug)
        parsed_jobs = []

        try:
            response = await client.get(url, timeout=self.timeout)
            if response.status_code == 404:
                logger.warning("Greenhouse board not found for %s (%s)", company.get("name"), slug)
                return []
            response.raise_for_status()

            payload = response.json()
            raw_jobs = payload.get("jobs", [])

            for j in raw_jobs:
                external_id = str(j.get("id"))
                title = j.get("title", "").strip()
                if not title:
                    continue

                location_data = j.get("location", {})
                raw_loc = location_data.get("name") if isinstance(location_data, dict) else str(location_data)

                departments = j.get("departments", [])
                dept_name = departments[0].get("name") if departments and isinstance(departments[0], dict) else ""

                content_raw = j.get("content", "")
                content_html = unescape(content_raw) if content_raw else ""
                content_text = clean_html(content_html)

                apply_url = j.get("absolute_url") or f"https://boards.greenhouse.io/{slug}/jobs/{external_id}"

                parsed_jobs.append({
                    "external_id": external_id,
                    "title": title,
                    "company_name": company.get("name"),
                    "company_slug": slug,
                    "company_logo": company.get("logo"),
                    "ats_type": "greenhouse",
                    "raw_location": raw_loc or "Remote",
                    "department": dept_name,
                    "apply_url": apply_url,
                    "description_html": content_html,
                    "description_text": content_text,
                    "updated_at": j.get("updated_at")
                })

        except Exception as e:
            logger.error("Error fetching Greenhouse jobs for %s: %s", company.get("name"), str(e))

        return parsed_jobs
