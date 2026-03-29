import csv
import smtplib
import time
import os
import json
import random
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ════════════════════════════════════════════════
#  CONFIG
# ════════════════════════════════════════════════

SMTP_HOST      = "smtp.hostinger.com"
SMTP_PORT      = 465
STUDENTS_FILE  = "data/students.csv"
SENT_LOG       = "output/sent_log.txt"
ERROR_LOG      = "output/error_log.txt"
START_DATE     = "2026-03-29"   # ← Your Day 1 (today)

EMAIL_SUBJECT = "Quick question for {name}"

EMAIL_BODY = """Hi {name},

Hope your time at {college} is going well.

I'm Vishnu, and I work with a small team helping students
get hands-on experience in {domain} through real project work.

We have a few spots opening up and thought this might be
relevant for you.

Would it be okay if I shared more details?

Vishnu
vaultsphereai.in"""

# ════════════════════════════════════════════════
#  WARM-UP DAILY LIMIT (Total emails per day)
# ════════════════════════════════════════════════

def get_warmup_limit():
    start  = datetime.date.fromisoformat(START_DATE)
    today  = datetime.date.today()
    day_no = (today - start).days + 1

    if   day_no <= 3:   limit = 30
    elif day_no <= 7:   limit = 100
    elif day_no <= 14:  limit = 500
    elif day_no <= 21:  limit = 1500
    elif day_no <= 30:  limit = 4000
    else:               limit = 7000   # Full capacity

    print(f"Day {day_no} of warm-up → Total limit today: {limit} emails")
    return limit, day_no

# ════════════════════════════════════════════════
#  LOAD ACCOUNTS FROM SECRET
# ════════════════════════════════════════════════

def load_accounts():
    raw = os.environ.get("EMAIL_ACCOUNTS", "[]")
    accounts = json.loads(raw)

    # Validate each account has required fields
    valid = []
    for acc in accounts:
        if "user" in acc and "pass" in acc and "limit" in acc:
            valid.append(acc)
        else:
            print(f"⚠️  Skipping invalid account entry: {acc}")

    print(f"✅ Loaded {len(valid)} valid email accounts")
    for i, acc in enumerate(valid):
        print(f"  Account {i+1}: {acc['user']} | Limit: {acc['limit']}")

    return valid

# ════════════════════════════════════════════════
#  LOAD STUDENTS (Multi-column CSV format)
# ════════════════════════════════════════════════

def load_students():
    students = []
    seen     = set()

    with open(STUDENTS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in reader.fieldnames:
                val = row.get(col, "").strip()
                # Valid email check
                if "@" in val and "." in val and val not in seen:
                    seen.add(val)
                    students.append({
                        "email":   val,
                        "name":    val.split("@")[0].replace(".", " ").capitalize(),
                        "college": col.strip(),
                        "domain":  "Technology"
                    })

    print(f"✅ Total unique students: {len(students)}")
    return students

# ════════════════════════════════════════════════
#  SENT LOG
# ════════════════════════════════════════════════

def load_sent():
    os.makedirs("output", exist_ok=True)
    try:
        with open(SENT_LOG, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def mark_sent(email):
    with open(SENT_LOG, "a") as f:
        f.write(email.strip() + "\n")

def log_error(email, error):
    with open(ERROR_LOG, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {email} | {error}\n")

# ════════════════════════════════════════════════
#  SEND ONE EMAIL
# ════════════════════════════════════════════════

def send_one(from_email, from_pass, student):
    subject = EMAIL_SUBJECT.format(name=student["name"])
    body    = EMAIL_BODY.format(
                name    = student["name"],
                college = student["college"],
                domain  = student["domain"]
              )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_email
    msg["To"]      = student["email"]
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.login(from_email, from_pass)
        server.sendmail(from_email, student["email"], msg.as_string())

# ════════════════════════════════════════════════
#  MAIN AGENT — Fixed Rotation Logic
# ════════════════════════════════════════════════

def run():
    warmup_limit, day_no = get_warmup_limit()
    accounts             = load_accounts()
    students             = load_students()
    already_sent         = load_sent()

    # Filter only pending students
    pending = [s for s in students if s["email"] not in already_sent]
    print(f"\nAlready sent : {len(already_sent)}")
    print(f"Pending      : {len(pending)}")
    print(f"Today's max  : {warmup_limit}")

    if not pending:
        print("✅ All students already emailed!")
        return

    # Today's batch = minimum of pending and warmup limit
    todays_batch = pending[:warmup_limit]
    print(f"Sending to   : {len(todays_batch)} students today\n")

    # ── Rotation Setup ──────────────────────────────
    # Track how many sent per account individually
    acc_sent_counts = [0] * len(accounts)
    acc_index       = 0   # Start with first account
    total_sent      = 0
    total_failed    = 0

    for student in todays_batch:

        # ── Find next available account ─────────────
        # Skip accounts that hit their individual limit
        while acc_index < len(accounts):
            current_acc   = accounts[acc_index]
            current_limit = current_acc["limit"]
            current_sent  = acc_sent_counts[acc_index]

            if current_sent < current_limit:
                break   # This account still has capacity
            else:
                print(f"🔄 Account {acc_index+1} ({current_acc['user']}) hit limit ({current_limit}). Switching...")
                acc_index += 1

        # ── All accounts exhausted for today ────────
        if acc_index >= len(accounts):
            print("⚠️  All accounts hit their daily limits. Stopping for today.")
            break

        account = accounts[acc_index]

        # ── Send email ───────────────────────────────
        try:
            send_one(account["user"], account["pass"], student)
            mark_sent(student["email"])
            acc_sent_counts[acc_index] += 1
            total_sent += 1

            print(f"[{total_sent:04d}] ✅ Sent → {student['name']:<20} | "
                  f"Account {acc_index+1} ({acc_sent_counts[acc_index]}/{account['limit']})")

        except smtplib.SMTPAuthenticationError:
            print(f"❌ AUTH FAILED for account {account['user']} — skipping this account")
            log_error(student["email"], f"Auth failed: {account['user']}")
            acc_index += 1   # Skip broken account entirely

        except smtplib.SMTPException as e:
            total_failed += 1
            log_error(student["email"], str(e))
            print(f"❌ SMTP Error → {student['email']} | {e}")
            time.sleep(5)

        except Exception as e:
            total_failed += 1
            log_error(student["email"], str(e))
            print(f"❌ Failed → {student['email']} | {e}")

        # ── Human-like delay ─────────────────────────
        time.sleep(random.uniform(8, 15))

    # ── Final Report ─────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  Day {day_no} Complete — {datetime.date.today()}")
    print(f"{'='*50}")
    print(f"  Sent today     : {total_sent}")
    print(f"  Failed         : {total_failed}")
    print(f"  Total sent ever: {len(already_sent) + total_sent}")
    print(f"  Remaining      : {len(pending) - total_sent}")
    print(f"{'='*50}")

    # Per-account breakdown
    print("\n  Account Breakdown:")
    for i, acc in enumerate(accounts):
        if acc_sent_counts[i] > 0:
            print(f"  Account {i+1}: {acc['user']} → sent {acc_sent_counts[i]}")

if __name__ == "__main__":
    run()
