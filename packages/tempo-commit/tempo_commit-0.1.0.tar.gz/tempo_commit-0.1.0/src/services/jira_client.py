from datetime import datetime
from src.config import get_settings

from jira import JIRA
from jira.resources import Issue

settings = get_settings()


class JIRAClient:
    def __init__(self) -> None:
        self.jira = JIRA(
            server=settings.jira_url,
            basic_auth=(settings.jira_email, settings.jira_api_token),
        )

    def get_issue_id(self, issue_key: str):
        return self.jira.issue(issue_key).id

    def get_account_id(self):
        myself = self.jira.myself()
        return myself.get("accountId")

    def extract_in_progress_transition_timestamp(self, issue_key: str):
        # TODO think of more reliable way?
        issue: Issue = self.jira.issue(issue_key)
        return datetime.strptime(
            issue.fields.statuscategorychangedate,
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )
