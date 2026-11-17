"""Core data classes for the gradebook: Student, Course and Enrollment."""

from .validators import (
    parse_course_code,
    parse_grade,
    parse_student_id,
    require_non_empty,
)


class Student:
    """A student with a unique numeric id and a name."""

    def __init__(self, student_id, name):
        """Create a student, checking that the id and name are valid."""
        self.id = parse_student_id(student_id)
        self.name = require_non_empty(name, "Student name")

    def to_dict(self):
        """Return the student as a plain dictionary for saving to JSON."""
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data):
        """Create a Student from a dictionary loaded from JSON."""
        return cls(data["id"], data["name"])

    def __str__(self):
        """Return a readable text version, e.g. '[1] Alice'."""
        return f"[{self.id}] {self.name}"


class Course:
    """A course with a unique code (e.g. CS101) and a title."""

    def __init__(self, code, title):
        """Create a course, checking that the code and title are valid."""
        self.code = parse_course_code(code)
        self.title = require_non_empty(title, "Course title")

    def to_dict(self):
        """Return the course as a plain dictionary for saving to JSON."""
        return {"code": self.code, "title": self.title}

    @classmethod
    def from_dict(cls, data):
        """Create a Course from a dictionary loaded from JSON."""
        return cls(data["code"], data["title"])

    def __str__(self):
        """Return a readable text version, e.g. 'CS101: Intro to CS'."""
        return f"{self.code}: {self.title}"


class Enrollment:
    """Links one student to one course and stores that student's grades."""

    def __init__(self, student_id, course_code, grades=None):
        """Create an enrollment; every grade must be a number from 0 to 100."""
        self.student_id = parse_student_id(student_id)
        self.course_code = parse_course_code(course_code)
        self.grades = [parse_grade(grade) for grade in (grades or [])]

    def add_grade(self, grade):
        """Check a grade and add it to this enrollment's list of grades."""
        self.grades.append(parse_grade(grade))

    def to_dict(self):
        """Return the enrollment as a plain dictionary for saving to JSON."""
        return {
            "student_id": self.student_id,
            "course_code": self.course_code,
            "grades": list(self.grades),
        }

    @classmethod
    def from_dict(cls, data):
        """Create an Enrollment from a dictionary loaded from JSON."""
        return cls(data["student_id"], data["course_code"], data.get("grades", []))

    def __str__(self):
        """Return a readable text version including the grades."""
        if self.grades:
            grades_text = ", ".join(f"{grade:g}" for grade in self.grades)
        else:
            grades_text = "no grades yet"
        return (
            f"Student {self.student_id} in {self.course_code}"
            f" - grades: {grades_text}"
        )