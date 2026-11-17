"""Small helper functions that check and clean user input.

Each helper either returns a clean value or raises ValueError
with a friendly message that the CLI can show to the user.
"""


def require_non_empty(value, field_name):
    """Return the text without extra spaces, or raise ValueError if empty.

    Args:
        value: The value to check (should be a string).
        field_name: A name used in the error message, e.g. "Student name".
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must not be empty.")
    return value.strip()


def parse_grade(value):
    """Convert a value to a grade (float) between 0 and 100.

    Raises:
        ValueError: If the value is not a number or is outside 0-100.
    """
    if isinstance(value, bool):
        raise ValueError(f"Grade must be a number, got {value!r}.")
    try:
        grade = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Grade must be a number, got {value!r}.") from None
    if not 0 <= grade <= 100:
        raise ValueError(f"Grade must be between 0 and 100, got {grade:g}.")
    return grade


def parse_student_id(value):
    """Convert a value to a positive whole-number student id.

    Raises:
        ValueError: If the value is not a whole number of 1 or more.
    """
    if isinstance(value, bool):
        raise ValueError(f"Student id must be a whole number, got {value!r}.")
    try:
        student_id = int(str(value).strip())
    except ValueError:
        raise ValueError(
            f"Student id must be a whole number, got {value!r}."
        ) from None
    if student_id < 1:
        raise ValueError(f"Student id must be 1 or more, got {student_id}.")
    return student_id


def parse_course_code(value):
    """Return the course code in capital letters, e.g. 'cs101' -> 'CS101'.

    Raises:
        ValueError: If the code is empty.
    """
    return require_non_empty(value, "Course code").upper()