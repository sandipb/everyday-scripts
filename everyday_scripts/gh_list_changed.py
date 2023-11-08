#!/usr/bin/env python3
from github import Github
from prettytable import PrettyTable
from collections import defaultdict
from datetime import datetime
import click
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)


def filter_prs_by_month(prs, month: str) -> List:
    start_date = datetime.fromisoformat(f"{month}-01T00:00:00")
    end_date = datetime.fromisoformat(f"{month}-01T00:00:00").replace(month=start_date.month % 12 + 1)
    return [pr for pr in prs if start_date <= pr.closed_at < end_date]


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--repo", required=True, help='GitHub repository in "owner/repo" format.')
@click.option("--month", required=True, help="Month for which to list PRs in YYYY-MM format.")
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub Auth Token.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(repo: str, month: str, token: str, verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not token:
        logging.error("Auth token not provided. Exiting.")
        return

    g = Github(token)
    repo_obj = g.get_repo(repo)
    all_closed_prs = repo_obj.get_pulls(state="closed", sort="created", direction="desc")

    logging.debug(f"Fetching closed PRs for {repo} in {month}...")

    filtered_prs = filter_prs_by_month(all_closed_prs, month)

    logging.debug(f"Fetched {len(filtered_prs)} closed PRs.")

    file_to_prs: Dict[str, List[str]] = defaultdict(list)

    for i, pr in enumerate(filtered_prs):
        logging.debug(f"Processing PR {i + 1}/{len(filtered_prs)}...")

        pr_title = pr.title
        files = pr.get_files()

        for file in files:
            if file.status == "added":
                file_to_prs[file.filename].append(pr_title)

    logging.debug(f"Found {len(file_to_prs)} new files.")

    sorted_files = sorted(file_to_prs.items())

    table = PrettyTable()
    table.field_names = ["File Path", "PR Summary"]

    for filename, pr_titles in sorted_files:
        for pr_title in pr_titles:
            table.add_row([filename, pr_title])

    print(table)


if __name__ == "__main__":
    main()
