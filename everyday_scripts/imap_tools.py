#!/usr/bin/env python3
"""
This is a toolkit for various operations on IMAP servers. Each subcommand is a tool in this toolkit.
"""

import click
import imaplib
import logging
from contextlib import contextmanager
from typing import Generator, Optional, List, Tuple
from email.header import decode_header
from prettytable import PrettyTable
from collections import Counter
import email
import re
import urllib.request

from tqdm import tqdm

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Context manager for IMAP server connection
@contextmanager
def imap_connection(imap_server: str, username: str, password: str) -> Generator[imaplib.IMAP4, None, None]:
    """Context manager for connecting to an IMAP server.

    :param imap_server: IMAP server address
    :param username: Email username
    :param password: Email password
    """
    logger.debug(f"Connecting to IMAP server: {imap_server}")
    conn = imaplib.IMAP4_SSL(imap_server)
    logger.debug("Connected successfully.")
    conn.login(username, password)
    logger.debug(f"Logged in as {username}.")
    try:
        yield conn
    finally:
        conn.logout()
        logger.debug("Logged out.")


def match_email_against_patterns(header: str, patterns: List[str]) -> Tuple[bool, List[str]]:
    """Check if the given email matches any of the provided patterns."""
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(email_pattern, header)
    email = match.group() if match else ""

    matching_patterns = [pattern for pattern in patterns if re.search(pattern, email, re.IGNORECASE)]
    return bool(matching_patterns), matching_patterns


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-s",
    "--imap-server",
    required=True,
    help="IMAP server address. Can also be set via IMAP_TOOLKIT_IMAP_SERVER env var.",
    type=str,
    envvar="IMAP_TOOLKIT_IMAP_SERVER",
)
@click.option(
    "-u",
    "--username",
    required=True,
    help="Email username. Can also be set via IMAP_TOOLKIT_USERNAME env var.",
    type=str,
    envvar="IMAP_TOOLKIT_USERNAME",
)
@click.option(
    "-p",
    "--password",
    required=True,
    help="Email password. Can also be set via IMAP_TOOLKIT_PASSWORD env var.",
    type=str,
    envvar="IMAP_TOOLKIT_PASSWORD",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output. Can also be set via IMAP_TOOLKIT_VERBOSE env var.",
    type=bool,
    envvar="IMAP_TOOLKIT_VERBOSE",
)
@click.pass_context
def cli(ctx: click.Context, imap_server: str, username: str, password: str, verbose: bool) -> None:
    """Toolkit for various operations on IMAP servers."""
    ctx.ensure_object(dict)
    ctx.obj["IMAP_SERVER"] = imap_server
    ctx.obj["USERNAME"] = username
    ctx.obj["PASSWORD"] = password
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        logger.setLevel(logging.DEBUG)


@cli.command()
@click.option(
    "--top-count",
    default=5,
    help="Number of most common sender email addresses to display",
    type=int,
)
@click.option(
    "--max-emails",
    default=None,
    help="Maximum number of emails to analyze. If not specified, all unread emails will be analyzed.",
    type=int,
)
@click.pass_context
def stats_senders(ctx: click.Context, top_count: int, max_emails: Optional[int]) -> None:
    """Output the most common sender email addresses among unread messages."""
    imap_server = ctx.obj["IMAP_SERVER"]
    username = ctx.obj["USERNAME"]
    password = ctx.obj["PASSWORD"]

    with imap_connection(imap_server, username, password) as conn:
        logger.debug("Selecting the inbox.")
        status, _ = conn.select("inbox")
        if status == "OK":
            logger.debug("Inbox selected successfully.")
            status, msgnums = conn.search(None, "UNSEEN")
            msgnums = msgnums[0].split()
            msgnums = sorted(msgnums, reverse=True)  # latest emails first
            if max_emails is not None:
                msgnums = msgnums[:max_emails]
            logger.debug(f"Analyzing {len(msgnums)} unread messages.")
            if msgnums:
                email_counter = Counter()
                for num in tqdm(msgnums, desc="Processing emails", unit="email"):
                    status, msg_data = conn.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM)])")
                    if msg_data and msg_data[0] is not None:
                        raw_email = msg_data[0][1]
                    else:
                        continue
                    msg = email.message_from_bytes(raw_email)  # type: ignore
                    from_header = decode_header(msg["From"])[0][0]
                    sender_email = re.search(
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                        from_header.decode(errors="ignore") if isinstance(from_header, bytes) else from_header,
                    )

                    if sender_email:
                        email_counter[sender_email.group()] += 1

                # Show top sender email addresses in PrettyTable
                x = PrettyTable()
                x.field_names = ["Email Address", "Count"]
                for email_addr, count in email_counter.most_common(top_count):
                    x.add_row([email_addr, count])
                print(x)
            else:
                click.echo("No unread messages found.")
        else:
            logger.debug("Failed to select the inbox.")
            click.echo("Failed to select the inbox.")


@cli.command()
@click.option(
    "-f",
    "--file-path",
    type=str,
    help="Path to a file containing list of regexes for email addresses.",
)
@click.option(
    "-u",
    "--url-path",
    type=str,
    help="URL to a document containing list of regexes for email addresses.",
)
@click.option(
    "-a",
    "--allow-all",
    is_flag=True,
    help="Delete all matching emails without prompting.",
)
@click.option(
    "-m",
    "--max-process",
    type=int,
    default=None,
    help="Maximum number of unread emails to process.",
)
@click.option("-n", "--no-progress", is_flag=True, help="Disable the progress meter.")
@click.pass_context
def delete_matching(
    ctx: click.Context,
    file_path: Optional[str],
    url_path: Optional[str],
    allow_all: bool,
    max_process: Optional[int],
    no_progress: bool,
) -> None:
    """Delete unread emails where the sender matches any of the given patterns."""
    deleted_count: int = 0
    processed_count: int = 0
    if file_path is None and url_path is None:
        click.echo("Either --file-path or --url-path must be specified.")
        return

    patterns = []
    if file_path:
        with open(file_path, "r") as f:
            file_patterns = [line.strip() for line in f.read().splitlines() if line.strip()]
            patterns.extend(file_patterns)
            logger.debug(f"Loaded {len(file_patterns)} patterns from {file_path}.")
    if url_path:
        with urllib.request.urlopen(url_path) as u:
            url_patterns = [line.strip() for line in u.read().decode().splitlines() if line.strip()]
            patterns.extend(url_patterns)
            logger.debug(f"Loaded {len(url_patterns)} patterns from {url_path}.")
    logger.debug(f"Total number of patterns: {len(patterns)}")

    imap_server = ctx.obj["IMAP_SERVER"]
    username = ctx.obj["USERNAME"]
    password = ctx.obj["PASSWORD"]

    with imap_connection(imap_server, username, password) as conn:
        status, data = conn.select("inbox")
        if status != "OK":
            click.echo("Failed to select the inbox.")
            return

        status, msgnums = conn.search(None, "UNSEEN")
        msgnums = msgnums[0].split()
        if max_process:
            msgnums = sorted(msgnums, reverse=True)[:max_process]

        if allow_all and not no_progress:  # Only show progress indicator if --allow-all is set and --no-progress is not set
            msgnums_iter = tqdm(msgnums, desc="Processing emails", unit="email")
        else:
            msgnums_iter = msgnums  # No progress indicator for interactive mode

        for num in msgnums_iter:
            processed_count += 1
            try:
                status, msg_data = conn.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
                if status != "OK":
                    logger.warning(f"Error fetching email {num}: {msg_data}")
                    continue  # Skip this iteration and move to the next email
            except imaplib.IMAP4.error as e:
                logger.warning(f"IMAP error while fetching email {num}: {e}")
                continue  # Skip this iteration and move to the next email

            raw_email = msg_data[0][1]  # type: ignore
            msg = email.message_from_bytes(raw_email)  # type: ignore

            from_header = decode_header(msg["From"])[0][0]
            # print(num, from_header)
            from_header = from_header.decode(errors="ignore") if isinstance(from_header, bytes) else from_header

            subject_header = msg.get("Subject", "")  # Use an empty string as default if "Subject" is None
            if subject_header is not None:
                subject_header = decode_header(subject_header)[0][0]
                if isinstance(subject_header, bytes):
                    subject_header = subject_header.decode(errors="ignore")

            matched, matching_patterns = match_email_against_patterns(from_header, patterns)
            if matched:
                logger.debug(f"Matching pattern for header [{from_header}]: [{','.join(matching_patterns)}]")
                colored_from_header = click.style(from_header, fg="green")
                colored_subject_header = click.style(subject_header, fg="yellow")
                deleted = False
                if not allow_all:
                    if click.confirm(f"Do you want to delete email from {colored_from_header} with subject {colored_subject_header}?"):
                        conn.store(num, "+FLAGS", "(\\Deleted)")
                        conn.expunge()
                        deleted_count += 1
                        deleted = True

                else:
                    conn.store(num, "+FLAGS", "(\\Deleted)")
                    conn.expunge()
                    deleted_count += 1
                    deleted = True

                if deleted:  # and not isinstance(msgnums_iter, tqdm):
                    click.echo(f"Email from {colored_from_header} with subject {colored_subject_header} deleted.")
    colored_processed_count = click.style(str(processed_count), fg="blue")
    colored_deleted_count = click.style(str(deleted_count), fg="red")

    click.echo(
        f"Total emails processed: {colored_processed_count}, Total emails deleted: {colored_deleted_count}"
    )  # Updated line to show colored counts


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("Operation cancelled by user. Exiting.")
