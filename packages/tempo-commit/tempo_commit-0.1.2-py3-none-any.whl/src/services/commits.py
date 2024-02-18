import re
import sys
from datetime import datetime
from typing import Optional

from git import Repo
from loguru import logger

from src.services.jira_client import JIRAClient
from src.services.tempo_client import TempoAPIClient


def get_issue_key_and_message_from_commit(message: str):
    jira_issue, commit_msg = message.split(" ", 1)
    _, commit_msg = commit_msg.split(": ", 1)
    return jira_issue, commit_msg


def get_last_commit_datetime(issue_key: str) -> Optional[datetime]:
    try:
        repo = Repo(search_parent_directories=True)
        last_commit = repo.head.commit
        commit_issue_key, _ = get_issue_key_and_message_from_commit(last_commit.message)
        if commit_issue_key != issue_key:
            return None
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


def commit_and_add_worklog(message: str):
    pattern = r"^[A-Z]+-[0-9]+ [A-Za-z]+: .+$"
    if not re.match(pattern, message):
        logger.error("Invalid commit message format. Commit aborted.")
        sys.exit(1)

    jira_issue, commit_msg = get_issue_key_and_message_from_commit(message)

    jira = JIRAClient()
    tempo = TempoAPIClient()
    logger.info(f"Searching for latest commit with issue={jira_issue}...")
    started_at = get_last_commit_datetime(issue_key=jira_issue)
    if started_at is None:
        logger.info("No commits found, using ticket transition timestamp.")
        started_at = jira.extract_in_progress_transition_timestamp(jira_issue)

    time_spent = (datetime.now(tz=started_at.tzinfo) - started_at).total_seconds()
    try:
        logger.info("Adding worklog...")
        tempo.add_worklog(
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
