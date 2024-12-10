#!/usr/bin/env python3

import argparse
import calendar
import http.client
import imaplib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from typing import Any

from harvest import get_time_entries


def chatgpt(prompt: str, api_key: str) -> str:
    conn = http.client.HTTPSConnection("api.openai.com")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {"messages": [{"role": "user", "content": prompt}], "model": "gpt-4"}
    conn.request(
        "POST",
        "/v1/chat/completions",
        body=json.dumps(data),
        headers=headers,
    )
    response = conn.getresponse()
    if response.status == 200:
        msg = json.loads(response.read())
        return msg["choices"][0]["message"]["content"]
    raise Exception(f"Error: {response.status} {response.reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    account = os.environ.get("HARVEST_ACCOUNT_ID")
    parser.add_argument(
        "--harvest-account-id",
        default=account,
        required=account is None,
        help="Get one from https://id.getharvest.com/developers (env: HARVEST_ACCOUNT_ID)",
    )
    token = os.environ.get("HARVEST_BEARER_TOKEN")
    parser.add_argument(
        "--harvest-bearer-token",
        default=os.environ.get("HARVEST_BEARER_TOKEN"),
        required=token is None,
        help="Get one from https://id.getharvest.com/developers (env: HARVEST_BEARER_TOKEN)",
    )
    parser.add_argument(
        "--user",
        type=str,
        default=os.environ.get("HARVEST_USER"),
        help="user to filter for (env: HARVEST_USER)",
    )
    parser.add_argument(
        "--calendar-week",
        type=int,
        choices=range(1, 53),
        help="Month to generate report for (cal -w to see calendar weeks)",
    )
    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        help="Month to generate report for",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.today().year,
        help="Year to generate report for",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Project to generate report for",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["html", "pdf"],
        default="html",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file",
    )
    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=os.environ.get("OPENAI_API_KEY"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--imap-encryption",
        type=str,
        choices=["none", "ssl", "tls"],
        help="IMAP username",
    )
    parser.add_argument(
        "--imap-host",
        type=str,
        help="IMAP host",
    )
    parser.add_argument(
        "--imap-username",
        type=str,
        help="IMAP username",
    )
    parser.add_argument(
        "--mail-from",
        type=str,
        help="Mail from",
    )
    parser.add_argument(
        "--mail-to",
        type=str,
        help="Mail to",
    )
    parser.add_argument(
        "--mail-subject-weekly",
        type=str,
        default="Timesheet report for week $calendar_week, $year",
        help="Template for mail subject for weekly report",
    )
    parser.add_argument(
        "--mail-subject-monthly",
        type=str,
        default="Monthly timesheet summary for $month/$year",
        help="Template for mail subject for monthly report",
    )
    parser.add_argument(
        "--mail-body",
        type=str,
        default="Please find the timesheet report attached to this email.",
        help="Mail body",
    )
    parser.add_argument(
        "--imap-password",
        type=str,
        default=os.environ.get("IMAP_PASSWORD"),
        help="IMAP password",
    )
    parser.add_argument(
        "--imap-folder",
        type=str,
        default="Drafts",
        help="IMAP Draft folder",
    )
    parser.add_argument(
        "--gpt-prompt",
        type=str,
        default="""
cLan is a solution to build a decentral network based on NixOS nodes.
Write a short montly summary of my work on the cLan project based on my daily summaries without referring to concrete dates: \n
        """,
    )

    args = parser.parse_args()
    if args.calendar_week and args.month:
        print("Please specify either --calendar-week or --month")
        sys.exit(1)
    if args.calendar_week:
        d = f"{args.year}-W{args.calendar_week}"
        # start with monday
        args.start = datetime.strptime(d + "-1", "%Y-W%W-%w").strftime("%Y%m%d")
        # end with sunday
        args.end = datetime.strptime(d + "-0", "%Y-W%W-%w").strftime("%Y%m%d")
    elif args.month:
        _, last_day = calendar.monthrange(args.year, args.month)
        args.start = date(args.year, args.month, 1).strftime("%Y%m%d")
        args.end = date(args.year, args.month, last_day).strftime("%Y%m%d")

    if args.imap_host:
        if not args.imap_username:
            print("Please specify --imap-username")
            sys.exit(1)
        if not args.imap_password:
            print("Please specify --imap-password")
            sys.exit(1)

    return args


def save_to_drafts(args: argparse.Namespace, report: bytes) -> None:
    imap_func: Any[imaplib.IMAP4_SSL, imaplib.IMAP4] = imaplib.IMAP4
    if args.imap_encryption == "ssl":
        imap_func = imaplib.IMAP4_SSL
    with imap_func(host=args.imap_host) as imap:
        if args.imap_encryption == "starttls":
            imap.starttls()

        print("Logging into mailbox...")
        imap.login(args.imap_username, args.imap_password)

        # Create message
        message = MIMEMultipart()
        message["From"] = args.mail_from
        message["To"] = args.mail_to
        if args.calendar_week:
            subject = Template(args.mail_subject_weekly).substitute(
                dict(calendar_week=f"{args.calendar_week:02d}", year=args.year)
            )
        else:
            subject = Template(args.mail_subject_monthly).substitute(
                dict(month=f"{args.month:02d}", year=args.year)
            )
        message["Subject"] = subject
        message.attach(MIMEText(args.mail_body, "plain"))

        if args.format == "html":
            name = "report.html"
        else:  # args.format == "pdf":
            name = "report.pdf"

        part = MIMEApplication(report, Name=name)
        # After the file is closed
        part["Content-Disposition"] = f'attachment; filename="{name}"'
        message.attach(part)

        utf8_message = str(message).encode("utf-8")

        # select mailbox
        print(f"Selecting mailbox {args.imap_folder}...")
        imap.select(args.imap_folder)

        # Send message
        imap.append(
            args.imap_folder, "", imaplib.Time2Internaldate(time.time()), utf8_message
        )


def markdown_to_html(markdown: str) -> str:
    res = subprocess.run(
        ["pandoc", "-t", "html", "-f", "markdown"],
        input=markdown,
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    return res.stdout.strip()


def render_time_table(args: argparse.Namespace, entries: list[dict[str, Any]]) -> str:
    html = "<table>"
    html += "<colgroup><col width='20%'><col width='10%'><col width='70%'></colgroup>"
    html += "<tr><th>Date</th><th>Hours</th><th>Notes</th></tr>"
    for entry in entries:
        res = subprocess.run(
            ["pandoc", "-t", "html", "-f", "markdown"],
            input=entry["notes"],
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        )
        notes = res.stdout.strip()
        date = datetime.strptime(entry["spent_date"], "%Y-%m-%d")
        weekday = date.strftime("%A")
        html += f"<tr><td>{entry['spent_date']} ({weekday})</td><td>{entry['rounded_hours']}</td><td>{notes}</td></tr>\n"
    html += "</table>"
    return html


def render_weekly_html(args: argparse.Namespace, entries: list[dict[str, Any]]) -> str:
    title = f"Report for week {args.calendar_week:02d}, {args.year}"
    html = "<html>"
    html += "<head>"
    html += f"<title>{title}</title>"
    html += "</head>"
    html += "<body>"
    html += render_time_table(args, entries)
    html += "</body>"
    html += "</html>"
    return html


def render_monthly_summary_html(
    args: argparse.Namespace, entries: list[dict[str, Any]]
) -> str:
    prompt = args.gpt_prompt
    time_entries = ""
    for entry in entries:
        time_entries += f"Date: {entry['spent_date']}\nNotes: {entry['notes']}\n\n"
    prompt += time_entries

    timetable = render_time_table(args, entries)
    draft = "<!--\n"
    draft += timetable
    draft += "-->\n\n"

    if args.openai_api_key:
        draft += chatgpt(prompt, args.openai_api_key)

    editor = os.environ.get("EDITOR", "vim")

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf.write(draft.encode("utf-8"))
        tf.flush()
        print(f"Opening {tf.name} in {editor}...")
        subprocess.call([editor, tf.name])
        tf.seek(0)
        edited_text = tf.read().decode("utf-8")

    html = f"<h1> Monthly timesheet summary for {args.month:02d}/{args.year}</h1>\n"
    html += timetable
    html += markdown_to_html(edited_text)

    return html


def get_entries(args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = get_time_entries(
        args.harvest_account_id, args.harvest_bearer_token, args.start, args.end
    )
    filtered_entries = []
    for entry in sorted(entries, key=lambda x: x["spent_date"]):
        if args.project and args.project != entry["project"]["name"]:
            continue
        if args.user and args.user != entry["user"]["name"]:
            continue
        filtered_entries.append(entry)
    return filtered_entries


def main() -> None:
    args = parse_args()
    entries = get_entries(args)
    if len(entries) == 0:
        print("No entries found in time period. Skip report")
        sys.exit(1)
    if args.month:
        html = render_monthly_summary_html(args, entries)

    else:
        html = render_weekly_html(args, entries)
    if args.format == "html":
        output = html.encode("utf-8")
    elif args.format == "pdf":
        res = subprocess.run(
            ["pandoc", "-t", "pdf", "-f", "html"],
            input=html.encode("utf-8"),
            stdout=subprocess.PIPE,
            check=True,
        )
        output = res.stdout
    else:
        raise RuntimeError("Invalid format")

    if args.imap_host:
        save_to_drafts(args, output)
    elif args.output:
        with open(args.output, "wb") as f:
            f.write(output)
    else:
        sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
