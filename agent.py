import pandas as pd
import os

DATA_FILE = "data/student_data1.csv"

def extract_emails():
    df = pd.read_csv(DATA_FILE)

    emails = set()

    for column in df.columns:
        emails.update(df[column].dropna().astype(str))

    return list(emails)


def main():
    emails = extract_emails()

    print(f"Total emails extracted: {len(emails)}")

    # For now just show first 20 (testing phase)
    for e in emails[:20]:
        print(e)


if __name__ == "__main__":
    main()
