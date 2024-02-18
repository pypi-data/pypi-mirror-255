import re
import sys
from datetime import datetime
from typing import Optional

from git import Repo
from loguru import logger

from src.services.jira_client import JIRAClient
from src.services.tempo_client import TempoAPIClient


def get_last_commit_datetime() -> Optional[datetime]:
    try:
        repo = Repo(search_parent_directories=True)
        last_commit = repo.head.commit
        return last_commit.committed_datetime
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def make_commit(message: str) -> None:
    try:
        repo = Repo(search_parent_directories=True)
        repo.index.commit(message)
        logger.info("Commit successful.")
    except Exception as e:
        logger.error(f"Error: {e}")


def seconds_to_string(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    return f"{hours}h {minutes}m {seconds}s"


async def commit_and_add_worklog(message: str):
    pattern = r"^[A-Z]+-[0-9]+ [A-Za-z]+: .+$"
    if not re.match(pattern, message):
        logger.error("Invalid commit message format. Commit aborted.")
        sys.exit(1)

    jira_issue, commit_msg = message.split(" ", 1)
    _, commit_msg = commit_msg.split(": ", 1)

    jira = JIRAClient()
    tempo = TempoAPIClient()
    started_at = get_last_commit_datetime()
    if started_at is None:
        started_at = jira.extract_in_progress_transition_timestamp(jira_issue)

    time_spent = (datetime.now(tz=started_at.tzinfo) - started_at).total_seconds()
    try:
        await tempo.add_worklog(
            issue_id=jira.get_issue_id(jira_issue),
            account_id=jira.get_account_id(),
            description=commit_msg,
            time_spent=time_spent,
            started_at=started_at,
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    else:
        logger.info(f"Worklog has been added: {seconds_to_string(time_spent)}")
        make_commit(message=message)
        sys.exit(0)
