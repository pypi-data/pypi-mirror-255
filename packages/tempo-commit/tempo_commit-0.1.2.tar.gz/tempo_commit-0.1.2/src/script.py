from config import get_settings
from services.commits import commit_and_add_worklog

settings = get_settings()


def get_commit_message():
    with open(".git/COMMIT_EDITMSG", "r") as file:
        commit_message = file.read()
    return commit_message.strip()


def pre_commit():
    commit_message = get_commit_message()
    commit_and_add_worklog(message=commit_message)


if __name__ == "__main__":
    pre_commit()
