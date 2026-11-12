"""
validator.py - Validation engine (Flowchart 1)

Checks one contact (name, phone, email) and tells us whether it is valid.
The main function is validate_contact(). It returns a tuple:
    (True, "OK")            if the record is good
    (False, "reason text")  if any rule fails

Every reason starts with a short category like "Invalid Phone" or "Bad Email",
followed by the detail in brackets. The analytics module uses the category
to count the common data entry errors.
"""


def validate_name(name):
    """Step 1: name must not be blank or only spaces."""
    if len(name.strip()) > 0:
        return True, "OK"
    return False, "Missing Name"


def validate_phone(phone):
    """Step 2: exactly 10 digits and must start with 6, 7, 8 or 9."""
    phone = phone.strip()

    if phone == "":
        return False, "Missing Phone"
    if not phone.isdigit():
        return False, "Invalid Phone (digits only, no letters, spaces or symbols)"
    if len(phone) != 10:
        return False, f"Invalid Phone (must be exactly 10 digits, got {len(phone)})"
    if phone[0] not in "6789":
        return False, "Invalid Phone (must start with 6, 7, 8 or 9)"
    return True, "OK"


def validate_email(email):
    """Step 3: exactly one @, no spaces, something before @,
    and a domain with a period that is not the first or last character."""
    email = email.strip()

    if email == "":
        return False, "Missing Email"

    at_count = email.count("@")
    if at_count == 0:
        return False, "Bad Email (no @ symbol)"
    if at_count > 1:
        return False, "Bad Email (multiple @ symbols)"

    # split() with no argument breaks the text at any whitespace,
    # so more than one piece means there was a space inside the email
    if len(email.split()) > 1:
        return False, "Bad Email (contains spaces)"

    local_part, domain = email.split("@")

    if local_part == "":
        return False, "Bad Email (nothing before @)"
    if domain == "":
        return False, "Bad Email (nothing after @)"

    # domain[1:-1] removes the first and last character,
    # so a period found in it is not at the start or the end
    if "." not in domain[1:-1]:
        return False, "Bad Email (domain needs a period that is not first or last)"

    return True, "OK"


def validate_contact(name, phone, email):
    """Run the 3 checks one after the other (Flowchart 1).
    The first check that fails decides the reason."""
    # None can come from a short CSV row, treat it as empty text
    name = (name or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip()

    ok, reason = validate_name(name)
    if not ok:
        return False, reason

    ok, reason = validate_phone(phone)
    if not ok:
        return False, reason

    ok, reason = validate_email(email)
    if not ok:
        return False, reason

    return True, "OK"


def error_category(reason):
    """'Invalid Phone (must start with ...)' -> 'Invalid Phone'"""
    return reason.split(" (")[0]


if __name__ == "__main__":
    # quick manual check: python validator.py
    print(validate_contact("Aarav Sharma", "9876543210", "aarav.sharma@gmail.com"))
    print(validate_contact("Ananya Sen", "5551234567", "ananya.sen@gmail.com"))
    print(validate_contact("Vikram Singh", "9898989898", "vikram.singh@@gmail.com"))
