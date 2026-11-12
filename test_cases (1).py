"""
test_cases.py - Test all scenarios and print PASS / FAIL for each one.

Run it with:   python test_cases.py
Save proof:    python test_cases.py > proof/test_cases.txt
"""

from validator import validate_contact, error_category
from loader import load_contacts, find_duplicate, build_seen
import analytics

passed = 0
failed = 0


def show(title, ok, detail=""):
    """Print one test result and update the counters."""
    global passed, failed
    if ok:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    print(f"[{status}] {title}")
    if detail != "" and not ok:
        print("        ->", detail)


# ------------------------------------------------------------------
# Part 1 : validation tests
# each test: (description, name, phone, email, expected result, expected category)
# ------------------------------------------------------------------
validation_tests = [
    # normal values
    ("Normal valid record",                  "Aarav Sharma", "9876543210", "aarav.sharma@gmail.com", True,  "OK"),
    ("Valid email with subdomain",           "Neha Gupta",   "8765432109", "neha@mail.college.edu",  True,  "OK"),
    ("Spaces around fields are removed",     "  Asha  ",     " 9876543210 ", " asha@gmail.com ",     True,  "OK"),
    # name
    ("Name is empty",                        "",             "9123456780", "noname@gmail.com",       False, "Missing Name"),
    ("Name is only spaces",                  "     ",        "9123456780", "noname@gmail.com",       False, "Missing Name"),
    ("Boundary: name with 1 letter",         "A",            "9123456780", "a@gmail.com",            True,  "OK"),
    # phone
    ("Phone is missing",                     "Rahul Das",    "",           "rahul.das@college.edu",  False, "Missing Phone"),
    ("Phone starts with 5",                  "Ananya Sen",   "5551234567", "ananya.sen@gmail.com",   False, "Invalid Phone"),
    ("Phone starts with 0",                  "Test",         "0123456789", "test@gmail.com",         False, "Invalid Phone"),
    ("Phone has letters",                    "Test",         "98765abcde", "test@gmail.com",         False, "Invalid Phone"),
    ("Phone has a space inside",             "Test",         "98765 4321", "test@gmail.com",         False, "Invalid Phone"),
    ("Phone with +91 prefix",                "Test",         "+919876543210", "test@gmail.com",      False, "Invalid Phone"),
    ("Boundary: 9 digits (too short)",       "Test",         "987654321",  "test@gmail.com",         False, "Invalid Phone"),
    ("Boundary: 11 digits (too long)",       "Test",         "98765432101", "test@gmail.com",        False, "Invalid Phone"),
    ("Boundary: smallest valid 6000000000",  "Test",         "6000000000", "test@gmail.com",         True,  "OK"),
    ("Boundary: largest valid 9999999999",   "Test",         "9999999999", "test@gmail.com",         True,  "OK"),
    ("Boundary: 5999999999 just below 6",    "Test",         "5999999999", "test@gmail.com",         False, "Invalid Phone"),
    ("Phone starts with 7",                  "Test",         "7001122334", "test@gmail.com",         True,  "OK"),
    ("Phone starts with 8",                  "Test",         "8123456789", "test@gmail.com",         True,  "OK"),
    # email
    ("Email is missing",                     "Test",         "9876543210", "",                       False, "Missing Email"),
    ("Email has no @",                       "Test",         "9876543210", "testgmail.com",          False, "Bad Email"),
    ("Email has two @",                      "Vikram Singh", "9898989898", "vikram.singh@@gmail.com", False, "Bad Email"),
    ("Email has a space",                    "Aditya Joshi", "7890123456", "aditya joshi@gmail.com", False, "Bad Email"),
    ("Email has nothing before @",           "Test",         "9876543210", "@gmail.com",             False, "Bad Email"),
    ("Email has nothing after @",            "Siddharth Rao", "9112233445", "siddharth.rao@",        False, "Bad Email"),
    ("Domain has no period",                 "Arjun Kapoor", "9876501234", "arjun@kapoor",           False, "Bad Email"),
    ("Domain starts with a period",          "Test",         "9876543210", "test@.com",              False, "Bad Email"),
    ("Domain ends with a period",            "Test",         "9876543210", "test@gmail.",            False, "Bad Email"),
    ("Boundary: smallest valid email a@b.c", "Test",         "9876543210", "a@b.c",                  True,  "OK"),
    # which error is reported first
    ("All fields wrong: name is reported first", "",         "123",        "abc",                    False, "Missing Name"),
    ("Phone and email wrong: phone is reported first", "Test", "123",      "abc",                    False, "Invalid Phone"),
]

print("=" * 70)
print("PART 1 - VALIDATION TESTS  (validate_contact)")
print("=" * 70)
for title, name, phone, email, want_valid, want_reason in validation_tests:
    got_valid, got_reason = validate_contact(name, phone, email)
    ok = (got_valid == want_valid) and got_reason.startswith(want_reason)
    show(title, ok, f"expected {want_valid} / {want_reason}, got {got_valid} / {got_reason}")
    if ok:
        print(f"        result: {got_reason}")

# ------------------------------------------------------------------
# Part 2 : duplicate tests
# ------------------------------------------------------------------
print()
print("=" * 70)
print("PART 2 - DUPLICATE TESTS  (find_duplicate)")
print("=" * 70)
people = [{"id": 1, "name": "Aarav Sharma", "phone": "9876543210", "email": "aarav.sharma@gmail.com"}]
seen_phones, seen_emails = build_seen(people)

result = find_duplicate("9876543210", "sneha.roy@gmail.com", seen_phones, seen_emails)
show("Same phone, different email is a duplicate", result is not None and result.startswith("Duplicate Phone"), result)
if result:
    print("        result:", result)

result = find_duplicate("9123456780", "aarav.sharma@gmail.com", seen_phones, seen_emails)
show("Same email, different phone is a duplicate", result is not None and result.startswith("Duplicate Email"), result)

result = find_duplicate("9123456780", "AARAV.SHARMA@GMAIL.COM", seen_phones, seen_emails)
show("Same email in capital letters is a duplicate", result is not None and result.startswith("Duplicate Email"), result)

result = find_duplicate("9123456780", "new.student@gmail.com", seen_phones, seen_emails)
show("New phone and new email is accepted", result is None, result)

# ------------------------------------------------------------------
# Part 3 : the real contacts.csv file (20 rows)
# ------------------------------------------------------------------
print()
print("=" * 70)
print("PART 3 - LOADER AND ANALYTICS ON contacts.csv")
print("=" * 70)
students, rejected, total = load_contacts("contacts.csv")

show("Total rows read is 20", total == 20, total)
show("Valid rows accepted is 12", len(students) == 12, len(students))
show("Rejected rows is 8", len(rejected) == 8, len(rejected))
show("Valid + rejected = total", len(students) + len(rejected) == total)
show("Every student ID is unique", len(set(s["id"] for s in students)) == len(students))
show("No phone number repeats in clean data", len(set(s["phone"] for s in students)) == len(students))
show("No email repeats in clean data", len(set(s["email"].lower() for s in students)) == len(students))
show("Sneha Roy was rejected as duplicate phone",
     any(r["name"] == "Sneha Roy" and r["reason"].startswith("Duplicate Phone") for r in rejected))
show("Aarav Sharma (first owner of the phone) was kept",
     any(s["name"] == "Aarav Sharma" for s in students))

errors = analytics.count_error_types(rejected)
show("Error counts are correct",
     errors == {"Missing Name": 1, "Missing Phone": 1, "Invalid Phone": 1, "Bad Email": 4, "Duplicate Phone": 1},
     errors)

series = analytics.count_phone_series(students)
show("Phone series counts are correct", series == {"9": 4, "8": 4, "7": 2, "6": 2}, series)

domains = analytics.count_email_domains(students)
show("Email domain counts are correct",
     domains == {"@gmail.com": 4, "@outlook.com": 3, "@yahoo.com": 2,
                 "@yahoo.co.in": 1, "@domain.com": 1, "@rediffmail.com": 1},
     domains)

show("Series counts add up to the number of valid students", sum(series.values()) == len(students))
show("Domain counts add up to the number of valid students", sum(domains.values()) == len(students))

print()
print("=" * 70)
print(f"SUMMARY: {passed} passed, {failed} failed, {passed + failed} tests in total")
print("=" * 70)
