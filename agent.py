import pandas as pd
import os
import smtplib
from email.message import EmailMessage
import json
import time

DATA_FILE = "data/student_data1.csv"

# Load all accounts from secret
accounts = json.loads(os.getenv("EMAIL_ACCOUNTS"))


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

    email_index = 0

    for account in accounts:
        user = account["user"]
        password = account["pass"]
        limit = account["limit"]

        print(f"Using account: {user}")

        try:
            with smtplib.SMTP_SSL("smtp.hostinger.com", 465) as smtp:
                smtp.login(user, password)

                count = 0

                while count < limit and email_index < len(emails) and email_index < 40:
                    receiver = "yvishnuvardhan08@gmail.com"

                    msg = EmailMessage()
                    msg["Subject"] = subject
                    msg["From"] = user
                    msg["To"] = receiver
                    msg.set_content(body)

                    try:
                        smtp.send_message(msg)
                        print(f"Sent from {user} to {receiver}")
                        count += 1
                        email_index += 1
                        time.sleep(5)
                    except Exception as e:
                        print(f"Failed {receiver}: {e}")
                        email_index += 1

        except Exception as e:
            print(f"Login failed for {user}: {e}")

        if email_index >= 20:  # test only
            break


def main():
    emails = extract_emails()
    print(f"Total emails: {len(emails)}")

    send_emails(emails)


if __name__ == "__main__":
    main()
