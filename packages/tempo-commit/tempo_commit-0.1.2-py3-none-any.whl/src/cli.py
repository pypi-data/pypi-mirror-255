import asyncclick as click
from src.config import BASE_DIR


@click.command()
@click.option(
    "--jira-url",
    prompt="JIRA URL",
    required=True,
    help="Enter your jira's url. Example: 'https://jira.atlassian.com'",
)
@click.option(
    "--jira-api-token",
    prompt="JIRA API TOKEN",
    required=True,
    help="Create and add your personal access token. Read more: 'https://id.atlassian.com/manage-profile/security/api-tokens'",
)
@click.option(
    "--jira-email",
    prompt="JIRA EMAIL",
    required=True,
    help="Enter your email that you use for Jira",
)
@click.option(
    "--tempo-api-token",
    prompt="TEMPO API TOKEN",
    required=True,
    help="Generate and enter your Tempo API token (Read more: https://help.tempo.io/cloud/en/tempo-planner/developing-with-tempo/using-rest-api-integrations.html)'",
)
async def init(**kwargs):
    with open(BASE_DIR / ".env", "w") as f:
        f.writelines([f"{field.upper()}={value}\n" for field, value in kwargs.items()])


@click.command()
@click.option(
    "--message",
    required=True,
    help="Commit message in the format '<issue-key> <prefix>: <description>",
)
async def commit(message: str):
    if not (BASE_DIR / ".env").exists():
        raise click.UsageError(message="Set environment variables first! Use --init.")
    from src.services.commits import (
        commit_and_add_worklog,
    )

    await commit_and_add_worklog(message=message)


if __name__ == "__main__":
    commit(_anyio_backend="asyncio")
