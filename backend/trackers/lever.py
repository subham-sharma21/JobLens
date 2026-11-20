"""
Lever ATS API Tracker.
Queries: https://api.lever.co/v0/postings/{slug}
"""

from typing import Dict, Any, List
import httpx
import logging
from backend.trackers.base import BaseTracker
from backend.services.extractor import clean_html

logger = logging.getLogger("joblens.trackers.lever")


class LeverTracker(BaseTracker):
    BASE_URL = "https://api.lever.co/v0/postings/{slug}"

    async def fetch_jobs(self, client: httpx.AsyncClient, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        slug = company.get("slug")
        url = self.BASE_URL.format(slug=slug)
        parsed_jobs = []

        try:
            response = await client.get(url, timeout=self.timeout)
            if response.status_code == 404:
                logger.warning("Lever board not found for %s (%s)", company.get("name"), slug)
                return []
            response.raise_for_status()

            raw_jobs = response.json()
            if not isinstance(raw_jobs, list):
                return []

            for j in raw_jobs:
                external_id = str(j.get("id"))
                title = j.get("text", "").strip()
                if not title:
                    continue

                categories = j.get("categories", {})
                raw_loc = categories.get("location") or categories.get("allLocations", ["Remote"])[0] if isinstance(categories.get("allLocations"), list) and categories.get("allLocations") else categories.get("location")
                dept_name = categories.get("department") or categories.get("team") or ""

                content_text = j.get("descriptionPlain") or clean_html(j.get("description", ""))
                content_html = j.get("description", "")

                apply_url = j.get("hostedUrl") or j.get("applyUrl") or f"https://jobs.lever.co/{slug}/{external_id}"

                parsed_jobs.append({
                    "external_id": external_id,
                    "title": title,
                    "company_name": company.get("name"),
                    "company_slug": slug,
                    "company_logo": company.get("logo"),
                    "ats_type": "lever",
                    "raw_location": raw_loc or "Remote",
                    "department": dept_name,
                    "apply_url": apply_url,
                    "description_html": content_html,
                    "description_text": content_text,
                    "updated_at": j.get("createdAt")
                })

        except Exception as e:
            logger.error("Error fetching Lever jobs for %s: %s", company.get("name"), str(e))

        return parsed_jobs
