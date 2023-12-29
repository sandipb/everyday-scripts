#!/usr/bin/env python3
#
# Script to test sending mail to an smtp server

import smtplib
import argparse
from email.message import EmailMessage


def send_email(
    smtp_host: str, smtp_port: int, use_ssl: bool, username: str, password: str, sender: str, receiver: str, subject: str, body: str
) -> None:
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    if use_ssl:
        smtp_class = smtplib.SMTP_SSL
    else:
        smtp_class = smtplib.SMTP

    with smtp_class(smtp_host, smtp_port) as server:
        if not use_ssl:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)


def main():
    parser = argparse.ArgumentParser(description="Send a test email via SMTP")
    parser.add_argument("--host", required=True, help="SMTP host")
    parser.add_argument("--port", type=int, default=587, help="SMTP port")
    parser.add_argument("--use_ssl", action="store_true", help="Use SSL (default: False)")
    parser.add_argument("--username", help="SMTP username (optional)")
    parser.add_argument("--password", help="SMTP password (optional)")
    parser.add_argument("--sender", required=True, help="Email sender")
    parser.add_argument("--receiver", required=True, help="Email receiver")
    parser.add_argument("--subject", default="Test Email", help="Email subject")
    parser.add_argument("--body", default="This is a test email", help="Email body")

    args = parser.parse_args()

    send_email(args.host, args.port, args.use_ssl, args.username, args.password, args.sender, args.receiver, args.subject, args.body)


if __name__ == "__main__":
    main()
