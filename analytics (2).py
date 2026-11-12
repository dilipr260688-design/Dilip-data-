"""
analytics.py - Business Intelligence report (Flowchart 2)

Step 1  Load data      (read contacts.csv, validate, remove duplicates)
Step 2  Data accuracy  (valid / total * 100 and count of each error type)
Step 3  Cohort metrics (phone series and email domains, using dictionaries)
Step 4  Print report   (formatted summary on the console)

Run it directly:   python analytics.py
"""

from loader import load_contacts, CONTACTS_FILE
from validator import error_category

LINE = "=" * 55


def plural(count):
    """1 student / 2 students"""
    if count == 1:
        return "student"
    return "students"


def count_error_types(rejected):
    """{'Invalid Phone': 1, 'Bad Email': 4, ...}"""
    counts = {}
    for record in rejected:
        category = error_category(record["reason"])
        counts[category] = counts.get(category, 0) + 1
    return counts


def count_phone_series(students):
    """Count students by the first digit of the phone number."""
    counts = {"9": 0, "8": 0, "7": 0, "6": 0}
    for student in students:
        first_digit = student["phone"][0]
        if first_digit in counts:
            counts[first_digit] += 1
    return counts


def count_email_domains(students):
    """{'@gmail.com': 4, '@outlook.com': 3, ...}"""
    counts = {}
    for student in students:
        domain = "@" + student["email"].split("@")[1].lower()
        counts[domain] = counts.get(domain, 0) + 1
    return counts


def sort_by_count(counts):
    """Highest count first, names in A-Z order when the counts are equal."""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def print_report(students):
    """Print the executive summary.
    The data quality part comes from the raw contacts.csv file,
    the telecom and domain part comes from the students currently registered."""

    print(LINE)
    print("       STUDENT REGISTRATION - BUSINESS INTELLIGENCE")
    print(LINE)

    # ---- Step 1 and 2 : load the raw file and check the accuracy
    try:
        accepted, rejected, total = load_contacts(CONTACTS_FILE)
    except (FileNotFoundError, ValueError):
        accepted, rejected, total = None, None, 0
        print(f"({CONTACTS_FILE} could not be read, data quality skipped)")

    if accepted is not None:
        if total > 0:
            accuracy = len(accepted) / total * 100
        else:
            accuracy = 0.0
        print(f"Total Contacts Processed : {total}")
        print(f"Valid Registrations      : {len(accepted)}")
        print(f"Rejected Records         : {len(rejected)}")
        print(f"Data Quality Accuracy    : {accuracy:.1f}%")

        print("\n--- Data Entry Errors ---")
        errors = count_error_types(rejected)
        if errors:
            for category, count in sort_by_count(errors):
                print(f"  {category:<15}: {count}")
        else:
            print("  No errors found")

    print(f"\nStudents Currently Registered : {len(students)}")

    # ---- Step 3 : cohort metrics
    print("\n--- Telecom Network Breakdown ---")
    series = count_phone_series(students)
    for digit in ["9", "8", "7", "6"]:
        count = series[digit]
        if len(students) > 0:
            percent = count / len(students) * 100
        else:
            percent = 0.0
        print(f"  {digit}-Series : {count} {plural(count)} ({percent:.1f}%)")

    if len(students) > 0:
        biggest = sort_by_count(series)[0]
        print(f"  Largest segment: {biggest[0]}-Series")

    print("\n--- Top Email Domains ---")
    domains = count_email_domains(students)
    if domains:
        for domain, count in sort_by_count(domains):
            print(f"  {domain:<18}: {count} {plural(count)}")
    else:
        print("  No students registered")

    print(LINE)


if __name__ == "__main__":
    try:
        valid_students, rejected_rows, total_rows = load_contacts(CONTACTS_FILE)
    except FileNotFoundError:
        print(f"Error: {CONTACTS_FILE} was not found in this folder.")
    else:
        print_report(valid_students)
