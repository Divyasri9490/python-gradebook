"""Create sample gradebook data and save it to data/gradebook.json.

Run from the project folder:
    python scripts/seed.py

Warning: this replaces any existing data in data/gradebook.json.
"""

import sys
from pathlib import Path

# Make the project folder importable so "import gradebook" works
# when this file is run as a script from the project folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gradebook import service  # noqa: E402
from gradebook.storage import (  # noqa: E402
    DEFAULT_DATA_FILE,
    empty_data,
    save_data,
)


def build_sample_data():
    """Return a new gradebook with 3 students, 2 courses and some grades."""
    data = empty_data()

    alice = service.add_student(data, "Alice Johnson")
    bob = service.add_student(data, "Bob Smith")
    chitra = service.add_student(data, "Chitra Rao")

    service.add_course(data, "CS101", "Intro to CS")
    service.add_course(data, "MATH201", "Linear Algebra")

    sample_grades = [
        (alice, "CS101", [95, 88]),
        (alice, "MATH201", [78, 85]),
        (bob, "CS101", [72, 80, 91]),
        (chitra, "MATH201", [90, 94]),
    ]
    for student_id, course_code, grades in sample_grades:
        service.enroll(data, student_id, course_code)
        for grade in grades:
            service.add_grade(data, student_id, course_code, grade)

    return data


def main():
    """Build the sample data, save it and print a short summary."""
    data = build_sample_data()
    save_data(data)
    print(f"Saved sample data to {DEFAULT_DATA_FILE}")
    print(
        f"{len(data['students'])} students, {len(data['courses'])} courses, "
        f"{len(data['enrollments'])} enrollments."
    )


if __name__ == "__main__":
    main()