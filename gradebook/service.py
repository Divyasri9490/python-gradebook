"""Business logic for the gradebook.

Every function receives the gradebook data dictionary (see storage.py)
as its first argument and works only on that data, which keeps the
functions simple to test. Functions that change data modify the
dictionary in place; the caller is responsible for saving it.
"""

from .logger import get_logger
from .models import Course, Enrollment, Student
from .validators import parse_course_code, parse_student_id

logger = get_logger()

SORT_OPTIONS = ("name", "code")


class GradebookError(Exception):
    """Raised when an action breaks a gradebook rule (e.g. unknown id)."""


def _check_sort(sort_by):
    """Raise ValueError if sort_by is not None, 'name' or 'code'."""
    if sort_by is not None and sort_by not in SORT_OPTIONS:
        raise ValueError(f"Sort must be one of {', '.join(SORT_OPTIONS)}.")


def find_student(data, student_id):
    """Return the student with this id, or raise GradebookError."""
    student_id = parse_student_id(student_id)
    for student in data["students"]:
        if student.id == student_id:
            return student
    raise GradebookError(f"No student with id {student_id}.")


def find_course(data, course_code):
    """Return the course with this code, or raise GradebookError."""
    course_code = parse_course_code(course_code)
    for course in data["courses"]:
        if course.code == course_code:
            return course
    raise GradebookError(f"No course with code {course_code}.")


def find_enrollment(data, student_id, course_code):
    """Return the enrollment for this student and course.

    Raises:
        GradebookError: If the student or course is unknown, or the
            student is not enrolled in the course.
    """
    student = find_student(data, student_id)
    course = find_course(data, course_code)
    for enrollment in data["enrollments"]:
        if (enrollment.student_id == student.id
                and enrollment.course_code == course.code):
            return enrollment
    raise GradebookError(
        f"Student {student.id} is not enrolled in {course.code}."
    )


def add_student(data, name):
    """Add a new student and return their new id (highest id + 1)."""
    next_id = max((student.id for student in data["students"]), default=0) + 1
    student = Student(next_id, name)
    data["students"].append(student)
    logger.info("Added student %s.", student)
    return student.id


def add_course(data, code, title):
    """Add a new course and return its code (in capital letters).

    Raises:
        GradebookError: If a course with the same code already exists.
    """
    course = Course(code, title)
    if any(existing.code == course.code for existing in data["courses"]):
        raise GradebookError(f"Course {course.code} already exists.")
    data["courses"].append(course)
    logger.info("Added course %s.", course)
    return course.code


def enroll(data, student_id, course_code):
    """Enroll an existing student in an existing course.

    Raises:
        GradebookError: If the student or course is unknown, or the
            student is already enrolled in the course.
    """
    student = find_student(data, student_id)
    course = find_course(data, course_code)
    already_enrolled = any(
        enrollment.student_id == student.id
        and enrollment.course_code == course.code
        for enrollment in data["enrollments"]
    )
    if already_enrolled:
        raise GradebookError(
            f"Student {student.id} is already enrolled in {course.code}."
        )
    enrollment = Enrollment(student.id, course.code)
    data["enrollments"].append(enrollment)
    logger.info("Enrolled student %s in %s.", student.id, course.code)
    return enrollment


def add_grade(data, student_id, course_code, grade):
    """Add a grade (0-100) for an enrolled student and return it as a float.

    Raises:
        GradebookError: If the student is not enrolled in the course.
        ValueError: If the grade is not a number from 0 to 100.
    """
    enrollment = find_enrollment(data, student_id, course_code)
    enrollment.add_grade(grade)
    new_grade = enrollment.grades[-1]
    logger.info(
        "Added grade %g for student %s in %s.",
        new_grade,
        enrollment.student_id,
        enrollment.course_code,
    )
    return new_grade


def list_students(data, sort_by=None):
    """Return students sorted by id, or by name if sort_by is 'name'."""
    _check_sort(sort_by)
    if sort_by == "name":
        return sorted(
            data["students"],
            key=lambda student: (student.name.lower(), student.id),
        )
    return sorted(data["students"], key=lambda student: student.id)


def list_courses(data, sort_by=None):
    """Return courses sorted by code, or by title if sort_by is 'name'."""
    _check_sort(sort_by)
    if sort_by == "name":
        return sorted(
            data["courses"],
            key=lambda course: (course.title.lower(), course.code),
        )
    return sorted(data["courses"], key=lambda course: course.code)


def list_enrollments(data, sort_by=None):
    """Return enrollments sorted by student id then course code.

    If sort_by is 'name', sort by student name; if 'code', sort by
    course code first.
    """
    _check_sort(sort_by)
    if sort_by == "name":
        names = {student.id: student.name.lower() for student in data["students"]}
        return sorted(
            data["enrollments"],
            key=lambda item: (names.get(item.student_id, ""), item.course_code),
        )
    if sort_by == "code":
        return sorted(
            data["enrollments"],
            key=lambda item: (item.course_code, item.student_id),
        )
    return sorted(
        data["enrollments"],
        key=lambda item: (item.student_id, item.course_code),
    )


def compute_average(data, student_id, course_code):
    """Return the average grade of a student in one course.

    Raises:
        GradebookError: If the student is not enrolled or has no grades.
    """
    enrollment = find_enrollment(data, student_id, course_code)
    if not enrollment.grades:
        raise GradebookError(
            f"Student {enrollment.student_id} has no grades in "
            f"{enrollment.course_code} yet."
        )
    return sum(enrollment.grades) / len(enrollment.grades)


def compute_gpa(data, student_id):
    """Return the simple mean of a student's course averages.

    Courses with no grades yet are skipped.

    Raises:
        GradebookError: If the student is unknown or has no grades at all.
    """
    student = find_student(data, student_id)
    course_averages = [
        sum(enrollment.grades) / len(enrollment.grades)
        for enrollment in data["enrollments"]
        if enrollment.student_id == student.id and enrollment.grades
    ]
    if not course_averages:
        raise GradebookError(f"Student {student.id} has no grades yet.")
    return sum(course_averages) / len(course_averages)