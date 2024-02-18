from datetime import datetime

import requests

from src.config import get_settings

settings = get_settings()


class TempoAPIClient:
    BASE_URL = "https://api.tempo.io/4"

    def add_worklog(
        self,
        issue_id: int,
        account_id: str,
        description: str,
        time_spent: int,
        started_at: datetime,
    ):

        payload = {
            "attributes": [],
            "authorAccountId": account_id,
            "billableSeconds": None,
            "description": description,
            "issueId": issue_id,
            "remainingEstimateSeconds": None,
            "startDate": started_at.date().strftime("%Y-%m-%d"),
            "startTime": started_at.time().strftime("%H:%M:%S"),
            "timeSpentSeconds": time_spent,
        }
        headers = {"Authorization": f"Bearer {settings.tempo_api_token}"}
        response = requests.post(
            f"{self.BASE_URL}/worklogs", json=payload, headers=headers
        )
        response.raise_for_status()
