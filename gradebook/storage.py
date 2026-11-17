"""Saving and loading gradebook data as JSON.

The default file is data/gradebook.json in the project folder.
In memory the data is a dictionary with three lists of model objects:
{"students": [...], "courses": [...], "enrollments": [...]}.
"""

import json
from pathlib import Path

from .logger import get_logger
from .models import Course, Enrollment, Student

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "gradebook.json"

logger = get_logger()


class StorageError(Exception):
    """Raised when the data file cannot be read or written."""


def empty_data():
    """Return a new, empty gradebook data dictionary."""
    return {"students": [], "courses": [], "enrollments": []}


def load_data(path=DEFAULT_DATA_FILE):
    """Load gradebook data from a JSON file.

    If the file does not exist, an empty gradebook is returned.

    Raises:
        StorageError: If the file is not valid JSON or has the wrong shape.
    """
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except FileNotFoundError:
        logger.info("No data file at %s; starting with an empty gradebook.", path)
        return empty_data()
    except json.JSONDecodeError as error:
        logger.error("Invalid JSON in %s: %s", path, error)
        raise StorageError(
            f"The data file {path} is damaged (invalid JSON at line "
            f"{error.lineno}). Fix the file, or delete it to start empty."
        ) from error

    try:
        data = {
            "students": [Student.from_dict(item) for item in raw.get("students", [])],
            "courses": [Course.from_dict(item) for item in raw.get("courses", [])],
            "enrollments": [
                Enrollment.from_dict(item) for item in raw.get("enrollments", [])
            ],
        }
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        logger.error("Unexpected content in %s: %s", path, error)
        raise StorageError(
            f"The data file {path} has unexpected content: {error}"
        ) from error

    logger.info(
        "Loaded %s (%d students, %d courses, %d enrollments).",
        path,
        len(data["students"]),
        len(data["courses"]),
        len(data["enrollments"]),
    )
    return data


def save_data(data, path=DEFAULT_DATA_FILE):
    """Save gradebook data to a JSON file, creating its folder if needed.

    Raises:
        StorageError: If the file cannot be written.
    """
    path = Path(path)
    raw = {
        "students": [student.to_dict() for student in data["students"]],
        "courses": [course.to_dict() for course in data["courses"]],
        "enrollments": [
            enrollment.to_dict() for enrollment in data["enrollments"]
        ],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(raw, file, indent=2)
    except OSError as error:
        logger.error("Could not save %s: %s", path, error)
        raise StorageError(f"Could not save data to {path}: {error}") from error
    logger.info("Saved data to %s.", path)