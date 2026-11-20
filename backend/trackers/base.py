"""
Base tracker class defining interface for ATS job board crawlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
import logging

logger = logging.getLogger("joblens.trackers")


class BaseTracker(ABC):
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    @abstractmethod
    async def fetch_jobs(self, client: httpx.AsyncClient, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetches and returns parsed job dictionary records for a company.
        """
        pass
