import pandas as pd
import os
import smtplib
from email.message import EmailMessage
import time

DATA_FILE = "data/student_data1.csv"

EMAIL_USER = os.getenv("EMAIL_USER_1")
EMAIL_PASS = os.getenv("EMAIL_PASS_1")


def extract_emails():
    df = pd.read_csv(DATA_FILE)

    emails = set()
    for column in df.columns:
        emails.update(df[column].dropna().astype(str))

    return list(emails)


def send_emails(emails):
    subject = "Internship Opportunity"
    body = """Hello,

We are offering internship opportunities in Cybersecurity, AI/ML, and Web Development.

If interested, reply to this email.

Regards,
VaultSphere AI
"""

    with smtplib.SMTP_SSL("smtp.hostinger.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)

        for i, email in enumerate(emails[:10]):  # TEST: only 10
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = EMAIL_USER
            msg["To"] = email
            msg.set_content(body)

            try:
                smtp.send_message(msg)
                print(f"Sent to {email}")
                time.sleep(5)  # delay to avoid spam
            except Exception as e:
                print(f"Failed: {email} -> {e}")


def main():
    emails = extract_emails()
    print(f"Total emails: {len(emails)}")

    send_emails(emails)


if __name__ == "__main__":
    main()
