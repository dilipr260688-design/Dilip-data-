"""
loader.py - Data ingestion script

Reads contacts.csv, validates every row, rejects duplicates,
keeps the valid students in a list of dictionaries and writes
them to students_clean.csv.

Run it directly to see the ingestion log:   python loader.py
"""

import csv
from validator import validate_contact

CONTACTS_FILE = "contacts.csv"
CLEAN_FILE = "students_clean.csv"
FIELDS = ["id", "name", "phone", "email"]


def find_duplicate(phone, email, seen_phones, seen_emails):
    """Return the duplicate reason text, or None if the contact is new.
    seen_phones and seen_emails are dictionaries, so the lookup is fast."""
    if phone in seen_phones:
        return f"Duplicate Phone (already registered to {seen_phones[phone]})"
    if email.lower() in seen_emails:
        return f"Duplicate Email (already registered to {seen_emails[email.lower()]})"
    return None


def build_seen(students):
    """Make the seen_phones and seen_emails dictionaries from a student list."""
    seen_phones = {}
    seen_emails = {}
    for student in students:
        seen_phones[student["phone"]] = student["name"]
        # emails are compared in lowercase: A@x.com and a@x.com are the same
        seen_emails[student["email"].lower()] = student["name"]
    return seen_phones, seen_emails


def load_contacts(filename=CONTACTS_FILE):
    """Read the raw CSV file.
    Returns: students (valid list), rejected (list of dicts), total_rows"""
    students = []
    rejected = []
    total_rows = 0
    seen_phones = {}
    seen_emails = {}

    # utf-8-sig also works for CSV files saved from Excel (which add a BOM)
    with open(filename, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for column in ["name", "phone", "email"]:
            if reader.fieldnames is None or column not in reader.fieldnames:
                raise ValueError(f"Column '{column}' is missing in {filename}")

        for row in reader:
            total_rows += 1
            name = (row.get("name") or "").strip()
            phone = (row.get("phone") or "").strip()
            email = (row.get("email") or "").strip()

            # 1. field rules, 2. duplicate rules
            is_valid, reason = validate_contact(name, phone, email)
            if is_valid:
                reason = find_duplicate(phone, email, seen_phones, seen_emails)
                if reason is not None:
                    is_valid = False

            if is_valid:
                seen_phones[phone] = name
                seen_emails[email.lower()] = name
                students.append({"id": len(students) + 1,
                                 "name": name, "phone": phone, "email": email})
            else:
                rejected.append({"row": total_rows, "name": name,
                                 "phone": phone, "email": email, "reason": reason})

    return students, rejected, total_rows


def save_students(students, filename=CLEAN_FILE):
    """Write the student list to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for student in students:
            writer.writerow(student)


def load_students(filename=CLEAN_FILE):
    """Read students_clean.csv back into a list of dictionaries."""
    students = []
    with open(filename, newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            students.append({"id": int(row["id"]), "name": row["name"],
                             "phone": row["phone"], "email": row["email"]})
    return students


def print_ingestion_log(students, rejected, total_rows, filename=CONTACTS_FILE):
    print("=" * 62)
    print(f"INGESTION LOG  ({filename})")
    print("=" * 62)
    print(f"Total rows read      : {total_rows}")
    print(f"Valid rows accepted  : {len(students)}")
    print(f"Rejected rows        : {len(rejected)}")

    if rejected:
        print("\nReason for each rejected row:")
        for r in rejected:
            shown_name = r["name"] if r["name"] != "" else "(blank)"
            print(f"  Row {r['row']:>2} | {shown_name:<16} | {r['reason']}")


if __name__ == "__main__":
    try:
        students, rejected, total_rows = load_contacts()
    except FileNotFoundError:
        print(f"Error: {CONTACTS_FILE} was not found in this folder.")
    except ValueError as error:
        print("Error:", error)
    else:
        print_ingestion_log(students, rejected, total_rows)
        save_students(students)
        print(f"\n{len(students)} clean records saved to {CLEAN_FILE}")
