#!/usr/bin/env python3

import imaplib
import email
from email.message import EmailMessage
from collections import Counter
from prettytable import PrettyTable
import os
import argparse
from typing import List, Tuple
import logging


def download_emails(imap_server: str, username: str, password: str, num_emails: int) -> List[EmailMessage]:
    """
    Connects to the IMAP server and downloads the specified number of latest emails.

    :param imap_server: IMAP server address
    :param username: Email username
    :param password: Email password
    :param num_emails: Number of latest emails to download
    :return: List of email messages
    """

    logging.info("Connecting to IMAP server: %s", imap_server)
    server = imaplib.IMAP4_SSL(imap_server)
    server.login(username, password)
    server.select("inbox")

    if b"SORT" in server.capabilities:
        logging.info("Fetching email IDs using SORT command.")
        _, data = server.uid("sort", "(REVERSE DATE)", "UTF-8", "ALL")
    else:
        logging.info("Fetching email IDs using SEARCH command.")
        _, data = server.uid("search", None, "ALL")  # type: ignore

    email_ids = data[0].split()[-num_emails:]
    emails = []
    logging.info("Downloading %d emails...", len(email_ids))
    for idx, e_id in enumerate(email_ids, 1):
        _, data = server.uid("fetch", e_id, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        emails.append(email_message)
        if idx % 100 == 0:
            logging.info("Downloaded %d emails...", idx)
    server.logout()
    logging.info("Download complete.")
    return emails


def analyze_senders(emails: List[EmailMessage]) -> List[Tuple[str, int]]:
    """
    Analyzes the email data to identify the most frequent senders.

    :param emails: List of email messages
    :return: List of tuples containing sender and count, sorted by frequency
    """
    senders = [email.utils.parseaddr(email_message["From"])[1] for email_message in emails]  # type: ignore
    sender_counts = Counter(senders)
    return sender_counts.most_common()


def display_results(sender_counts: List[Tuple[str, int]]) -> None:
    """
    Displays the most frequent senders in a table format.

    :param sender_counts: List of tuples containing sender and count
    """
    table = PrettyTable(["Sender", "Count"])
    for sender, count in reversed(sender_counts):
        table.add_row([sender, count])
    print(table)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze the most frequent senders in an email inbox. "
        "You can provide the IMAP server, username, and password "
        "as command-line arguments or environment variables."
    )
    parser.add_argument("-s", "--server", default=os.environ.get("IMAP_SERVER"), help="IMAP server address (e.g., imap.example.com)")
    parser.add_argument("-u", "--username", default=os.environ.get("EMAIL_USERNAME"), help="Email username")
    parser.add_argument("-p", "--password", default=os.environ.get("EMAIL_PASSWORD"), help="Email password")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-n", "--num-emails", type=int, default=1000, help="Number of emails to analyze (default: 1000)")
    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s", datefmt="%b %d %H:%M:%S")

    try:
        imap_server = args.server if args.server else input("Enter IMAP server: ")
        username = args.username if args.username else input("Enter username: ")
        password = args.password if args.password else input("Enter password: ")
        num_emails = args.num_emails

        emails = download_emails(imap_server, username, password, num_emails)
        sender_counts = analyze_senders(emails)
        display_results(sender_counts)
    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt received. Exiting...")


if __name__ == "__main__":
    main()
