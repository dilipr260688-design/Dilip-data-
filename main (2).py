"""
main.py - Interactive Student Management Console

Menu:  1 View all   2 Search   3 Register   4 Update   5 Delete
       6 Analytics report   7 Save and exit

Run it with:   python main.py
"""

import os
from validator import validate_contact
from loader import (load_contacts, load_students, save_students,
                    build_seen, find_duplicate, CLEAN_FILE, CONTACTS_FILE)
import analytics


# ---------------------------------------------------------------- helper functions
def next_id(students):
    """The new ID is one more than the biggest ID, so old IDs are never reused."""
    biggest = 0
    for student in students:
        if student["id"] > biggest:
            biggest = student["id"]
    return biggest + 1


def find_student(students, key):
    """Find one student by ID or by phone number. Returns None if not found."""
    for student in students:
        if str(student["id"]) == key or student["phone"] == key:
            return student
    return None


def search_students(students, query):
    """Exact match for phone or email, part of the name is enough for name."""
    q = query.lower()
    results = []
    for student in students:
        if q == student["phone"] or q == student["email"].lower() or q in student["name"].lower():
            results.append(student)
    return results


def print_table(student_list):
    print()
    print(f"{'ID':<5}{'Name':<22}{'Phone':<13}{'Email'}")
    print("-" * 65)
    for s in student_list:
        print(f"{s['id']:<5}{s['name']:<22}{s['phone']:<13}{s['email']}")
    print("-" * 65)
    print(f"{len(student_list)} record(s)")


def check_new_values(students, name, phone, email, skip=None):
    """Validate the fields and check for duplicates.
    skip is the student being updated (so it is not compared with itself).
    Returns None if everything is fine, otherwise the reason text."""
    is_valid, reason = validate_contact(name, phone, email)
    if not is_valid:
        return reason

    others = [s for s in students if s is not skip]
    seen_phones, seen_emails = build_seen(others)
    return find_duplicate(phone, email, seen_phones, seen_emails)


# ---------------------------------------------------------------- menu options
def view_all(students):
    if len(students) == 0:
        print("\nNo students registered yet.")
        return
    print_table(students)


def search_record(students):
    query = input("Enter phone number, email or name to search: ").strip()
    if query == "":
        print("Nothing entered.")
        return

    results = search_students(students, query)
    if len(results) == 0:
        print("No student found for", query)
    else:
        print_table(results)


def register_student(students):
    print("\n--- Register New Student ---")
    name = input("Name  : ").strip()
    phone = input("Phone : ").strip()
    email = input("Email : ").strip()

    problem = check_new_values(students, name, phone, email)
    if problem is not None:
        print("Registration failed ->", problem)
        return

    student = {"id": next_id(students), "name": name, "phone": phone, "email": email}
    students.append(student)
    print(f"Student registered successfully with ID {student['id']}.")


def update_student(students):
    key = input("Enter student ID or phone number to update: ").strip()
    student = find_student(students, key)
    if student is None:
        print("No student found for", key)
        return

    print_table([student])
    print("\nWhat do you want to change?")
    print("  1. Name")
    print("  2. Phone")
    print("  3. Email")
    print("  0. Cancel")
    choice = input("Choice: ").strip()

    fields = {"1": "name", "2": "phone", "3": "email"}
    if choice == "0":
        print("Update cancelled.")
        return
    if choice not in fields:
        print("Invalid choice.")
        return

    field = fields[choice]
    new_value = input(f"New {field}: ").strip()

    # make the changed copy first and validate it, only then change the real record
    updated = dict(student)
    updated[field] = new_value
    problem = check_new_values(students, updated["name"], updated["phone"],
                               updated["email"], skip=student)
    if problem is not None:
        print("Update failed ->", problem)
        return

    old_value = student[field]
    student[field] = new_value
    print(f"{field.title()} updated: {old_value} -> {new_value}")


def delete_student(students):
    key = input("Enter student ID or phone number to delete: ").strip()
    student = find_student(students, key)
    if student is None:
        print("No student found for", key)
        return

    sure = input(f"Delete {student['name']} (ID {student['id']})? (y/n): ").strip().lower()
    if sure == "y":
        students.remove(student)
        print("Student deleted.")
    else:
        print("Delete cancelled.")


# ---------------------------------------------------------------- start and menu
def load_data():
    """Use students_clean.csv if it exists, otherwise build it from contacts.csv."""
    if os.path.exists(CLEAN_FILE):
        students = load_students(CLEAN_FILE)
        print(f"Loaded {len(students)} students from {CLEAN_FILE}")
        return students

    try:
        students, rejected, total = load_contacts(CONTACTS_FILE)
    except FileNotFoundError:
        print(f"{CONTACTS_FILE} not found. Starting with an empty list.")
        return []
    print(f"Read {total} rows from {CONTACTS_FILE}: {len(students)} valid, {len(rejected)} rejected")
    return students


def show_menu():
    print("\n====== STUDENT REGISTRATION SYSTEM ======")
    print(" 1. View All Students")
    print(" 2. Search Record")
    print(" 3. Register Student")
    print(" 4. Update Student")
    print(" 5. Delete Student")
    print(" 6. Analytics Report")
    print(" 7. Save and Exit")


def main():
    students = load_data()

    try:
        while True:
            show_menu()
            choice = input("Enter your choice (1-7): ").strip()

            if choice == "1":
                view_all(students)
            elif choice == "2":
                search_record(students)
            elif choice == "3":
                register_student(students)
            elif choice == "4":
                update_student(students)
            elif choice == "5":
                delete_student(students)
            elif choice == "6":
                print()
                analytics.print_report(students)
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 7.")
    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted.")

    save_students(students)
    print(f"{len(students)} records saved to {CLEAN_FILE}. Goodbye!")


if __name__ == "__main__":
    main()
