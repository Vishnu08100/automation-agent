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

SMTP_HOST           = "smtp.hostinger.com"
SMTP_PORT           = 465
START_DATE          = "2026-03-29"

TEST_MODE           = True   # True = only principals | False = both

STUDENTS_FILE       = "data/students.csv" if not TEST_MODE else ""
PRINCIPALS_FILE     = "data/principals.csv"

SENT_STUDENTS_LOG   = "output/sent_students.txt"
SENT_PRINCIPALS_LOG = "output/sent_principals.txt"
ERROR_LOG           = "output/error_log.txt"

# ════════════════════════════════════════════════
#  EMAIL TEMPLATES — HTML FORMAT
# ════════════════════════════════════════════════

STUDENT_SUBJECT = "Summer Short-Term Internship – Registrations Now Live | VaultSphere AI"

STUDENT_HTML = """
<html>
<body style="font-family: Arial, sans-serif; font-size: 15px; color: #222222; line-height: 1.7;">

<p>Dear Student,</p>

<p>Greetings from <strong>VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED!</strong></p>

<p>We are pleased to introduce our Industry-Integrated Short-Term Internship Program, designed to equip students with hands-on experience in emerging technologies and enhance their industry readiness.</p>

<p>🎓 SHORT-TERM INTERNSHIP ALERT FOR ENGINEERING &amp; DEGREE STUDENTS<br>
Registrations are now LIVE for our Summer Short-Term Internship Program 🚀</p>

<p>
- Program Details: <a href="https://vaultsphereai.in/internship/internship_registration.html">https://vaultsphereai.in/internship/internship_registration.html</a><br>
- Start Date: First week of May
</p>

<p><strong>💻 Available Domains:</strong></p>
<p>
AI &amp; ML<br>
Data Science<br>
Data Analytics<br>
Java Fullstack Development<br>
Web Development<br>
Python for AI &amp; Automation<br>
Cloud Computing &amp; DevOps<br>
Cybersecurity, Digital Forensics &amp; Social Media Forensics<br>
Embedded Systems<br>
IoT (Internet of Things)<br>
VLSI Designing<br>
Industrial Automation<br>
Power Generation, Transmission &amp; Distribution<br>
UI/UX Design &amp; Graphic Designing<br>
Digital Marketing<br>
SAP (R to R)<br>
Medical Coding
</p>

<p><strong>⏳ Duration: 2 Months | 2 Hours per Day</strong><br>
<strong>📜 Internship Certificate + Project Review</strong><br>
<strong>🤝 Placement Assistance &amp; Interview Opportunities</strong><br>
<strong>⚠️ Limited Slots – First Come First Serve</strong></p>

<p><strong>Note:</strong><br>
• Faculty members can also enrol in these programs<br>
• A Course Completion Certificate will be provided at a nominal fee<br>
• All sessions are conducted LIVE and are mentored by industry experts</p>

<p>We kindly request you to circulate this information among your students and encourage them to take advantage of this valuable opportunity.</p>

<p>For further details, please contact:<br>
• Support: <a href="mailto:support@vaultsphereai.com">support@vaultsphereai.com</a><br>
• Mobile: +91 9618013827, +91 8106975810</p>

<p><strong>HR Contact:</strong><br>
K S Deepthi<br>
HR Manager<br>
VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED<br>
📧 <a href="mailto:hr@vaultsphereai.com">hr@vaultsphereai.com</a><br>
📞 +91 7353078181<br>
🌐 <a href="http://www.vaultsphereai.in">www.vaultsphereai.in</a></p>

<p>We look forward to your support in empowering students with industry-relevant skills and improving their employability.</p>

<p>Warm regards,<br>
<strong>VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED</strong></p>

</body>
</html>
"""

# ────────────────────────────────────────────────

PRINCIPAL_SUBJECT = "Industry-Integrated Internship Program for Your Students – VaultSphere AI"

PRINCIPAL_HTML = """
<html>
<body style="font-family: Arial, sans-serif; font-size: 15px; color: #222222; line-height: 1.7;">

<p>Dear Sir/Madam,</p>

<p>Greetings from <strong>VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED!</strong></p>

<p>We are pleased to introduce our Industry-Integrated Short-Term Internship Program, designed to equip students with hands-on experience in emerging technologies and enhance their industry readiness.</p>

<p>🎓 SHORT-TERM INTERNSHIP ALERT FOR ENGINEERING &amp; DEGREE STUDENTS<br>
Registrations are now LIVE for our Summer Short-Term Internship Program 🚀</p>

<p>
- Program Details: <a href="https://vaultsphereai.in/internship/internship_registration.html">https://vaultsphereai.in/internship/internship_registration.html</a><br>
- Start Date: First week of May
</p>

<p><strong>💻 Available Domains:</strong></p>
<p>
AI &amp; ML<br>
Data Science<br>
Data Analytics<br>
Java Fullstack Development<br>
Web Development<br>
Python for AI &amp; Automation<br>
Cloud Computing &amp; DevOps<br>
Cybersecurity, Digital Forensics &amp; Social Media Forensics<br>
Embedded Systems<br>
IoT (Internet of Things)<br>
VLSI Designing<br>
Industrial Automation<br>
Power Generation, Transmission &amp; Distribution<br>
UI/UX Design &amp; Graphic Designing<br>
Digital Marketing<br>
SAP (R to R)<br>
Medical Coding
</p>

<p><strong>⏳ Duration: 2 Months | 2 Hours per Day</strong><br>
<strong>📜 Internship Certificate + Project Review</strong><br>
<strong>🤝 Placement Assistance &amp; Interview Opportunities</strong><br>
<strong>⚠️ Limited Slots – First Come First Serve</strong></p>

<p><strong>Note:</strong><br>
• Faculty members can also enrol in these programs<br>
• A Course Completion Certificate will be provided at a nominal fee<br>
• All sessions are conducted LIVE and are mentored by industry experts</p>

<p>We kindly request you to circulate this information among your students and encourage them to take advantage of this valuable opportunity.</p>

<p>For further details, please contact:<br>
• Support: <a href="mailto:support@vaultsphereai.com">support@vaultsphereai.com</a><br>
• Mobile: +91 9618013827, +91 8106975810</p>

<p><strong>HR Contact:</strong><br>
K S Deepthi<br>
HR Manager<br>
VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED<br>
📧 <a href="mailto:hr@vaultsphereai.com">hr@vaultsphereai.com</a><br>
📞 +91 7353078181<br>
🌐 <a href="http://www.vaultsphereai.in">www.vaultsphereai.in</a></p>

<p>We look forward to your support in empowering students with industry-relevant skills and improving their employability.</p>

<p>Warm regards,<br>
<strong>VAULTSPHERE AI TECHNOLOGIES PRIVATE LIMITED</strong></p>

</body>
</html>
"""

# ════════════════════════════════════════════════
#  WARM-UP LIMIT
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
    else:               limit = 5700

    print(f"Day {day_no} → Today's total limit: {limit}")
    return limit, day_no

# ════════════════════════════════════════════════
#  LOAD ACCOUNTS
# ════════════════════════════════════════════════

def load_accounts():
    raw      = os.environ.get("EMAIL_ACCOUNTS", "[]")
    accounts = json.loads(raw)
    valid    = [a for a in accounts if "user" in a and "pass" in a]
    print(f"Loaded {len(valid)} email accounts")
    return valid

# ════════════════════════════════════════════════
#  LOAD RECIPIENTS
# ════════════════════════════════════════════════

def load_recipients(filepath, mode):
    recipients = []
    seen       = set()

    if mode == "student":
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for col in reader.fieldnames:
                    val = row.get(col, "").strip()
                    if "@" in val and "." in val and val not in seen:
                        seen.add(val)
                        recipients.append({"email": val})

    elif mode == "principal":
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("email", "").strip()
                if "@" in email and "." in email and email not in seen:
                    seen.add(email)
                    recipients.append({"email": email})

    print(f"Loaded {len(recipients)} {mode} recipients")
    return recipients

# ════════════════════════════════════════════════
#  SENT LOG
# ════════════════════════════════════════════════

def load_sent(log_file):
    os.makedirs("output", exist_ok=True)
    try:
        with open(log_file) as f:
            return set(l.strip() for l in f if l.strip())
    except FileNotFoundError:
        return set()

def mark_sent(email, log_file):
    with open(log_file, "a") as f:
        f.write(email.strip() + "\n")

def log_error(email, error):
    os.makedirs("output", exist_ok=True)
    with open(ERROR_LOG, "a") as f:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{ts} | {email} | {error}\n")

# ════════════════════════════════════════════════
#  SEND ONE EMAIL
# ════════════════════════════════════════════════

def send_one(from_email, from_pass, to_email, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"VaultSphere AI <{from_email}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.login(from_email, from_pass)
        server.sendmail(from_email, to_email, msg.as_string())

# ════════════════════════════════════════════════
#  SEND BATCH
# ════════════════════════════════════════════════

def send_batch(accounts, recipients, sent_log, subject, html_body, label, limit):
    already_sent = load_sent(sent_log)
    pending      = [r for r in recipients if r["email"] not in already_sent]

    print(f"\n── {label.upper()} ──")
    print(f"  Already sent : {len(already_sent)}")
    print(f"  Pending      : {len(pending)}")
    print(f"  Today's limit: {limit}")

    if not pending:
        print(f"  All {label}s already emailed!")
        return 0

    batch        = pending[:limit]
    acc_index    = 0
    acc_sent     = [0] * len(accounts)
    total_sent   = 0
    total_failed = 0

    for recipient in batch:

        while acc_index < len(accounts):
            acc_limit = accounts[acc_index].get("limit", 100)
            if acc_sent[acc_index] < acc_limit:
                break
            print(f"  Account {acc_index+1} hit limit → switching")
            acc_index += 1

        if acc_index >= len(accounts):
            print(f"  All accounts exhausted for today.")
            break

        account = accounts[acc_index]
        email   = recipient["email"]

        try:
            send_one(account["user"], account["pass"], email, subject, html_body)
            mark_sent(email, sent_log)
            acc_sent[acc_index] += 1
            total_sent          += 1
            print(f"  [{total_sent:04d}] Sent → {email} "
                  f"| Acc {acc_index+1} "
                  f"({acc_sent[acc_index]}/{account.get('limit',100)})")

        except smtplib.SMTPAuthenticationError:
            print(f"  AUTH FAILED: {account['user']} → skipping")
            acc_index += 1

        except Exception as e:
            total_failed += 1
            log_error(email, str(e))
            print(f"  FAILED → {email} | {e}")

        time.sleep(random.uniform(8, 15))

    print(f"\n  Done → Sent: {total_sent} | Failed: {total_failed}")
    print(f"  Remaining tomorrow: {len(pending) - total_sent}")
    return total_sent

# ════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════

def run():
    warmup_limit, day_no = get_warmup_limit()
    accounts             = load_accounts()

    principal_limit = max(10, warmup_limit // 10)
    student_limit   = warmup_limit - principal_limit

    total = 0

    # Send to STUDENTS
    if STUDENTS_FILE and os.path.exists(STUDENTS_FILE):
        students = load_recipients(STUDENTS_FILE, "student")
        total += send_batch(accounts, students,
                            SENT_STUDENTS_LOG,
                            STUDENT_SUBJECT, STUDENT_HTML,
                            "student", student_limit)
    else:
        print("Skipping students (TEST_MODE or file not found)")

    # Send to PRINCIPALS
    if os.path.exists(PRINCIPALS_FILE):
        principals = load_recipients(PRINCIPALS_FILE, "principal")
        total += send_batch(accounts, principals,
                            SENT_PRINCIPALS_LOG,
                            PRINCIPAL_SUBJECT, PRINCIPAL_HTML,
                            "principal", principal_limit)
    else:
        print("data/principals.csv not found — skipping")

    print(f"\n{'='*50}")
    print(f"  Day {day_no} Complete | Total sent today: {total}")
    print(f"{'='*50}")

if __name__ == "__main__":
    run()
