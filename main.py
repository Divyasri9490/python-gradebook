"""Command-line interface for the gradebook.

Run from the project folder, for example:
    python main.py add-student --name "Alice"
    python main.py list students --sort name
    python main.py avg --student-id 1 --course CS101
"""

import argparse
import sys

from gradebook import service
from gradebook.logger import get_logger
from gradebook.storage import StorageError, load_data, save_data
from gradebook.validators import parse_course_code, parse_grade, parse_student_id

logger = get_logger()


def build_parser():
    """Create the argparse parser with one subcommand per action."""
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Gradebook: manage students, courses and grades.",
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="command"
    )

    add_student = subparsers.add_parser("add-student", help="Add a new student.")
    add_student.add_argument("--name", required=True, help="Student's name.")

    add_course = subparsers.add_parser("add-course", help="Add a new course.")
    add_course.add_argument("--code", required=True, help="Course code, e.g. CS101.")
    add_course.add_argument("--title", required=True, help="Course title.")

    enroll = subparsers.add_parser("enroll", help="Enroll a student in a course.")
    enroll.add_argument("--student-id", required=True, help="Student id.")
    enroll.add_argument("--course", required=True, help="Course code.")

    add_grade = subparsers.add_parser("add-grade", help="Add a grade (0-100).")
    add_grade.add_argument("--student-id", required=True, help="Student id.")
    add_grade.add_argument("--course", required=True, help="Course code.")
    add_grade.add_argument("--grade", required=True, help="Grade from 0 to 100.")

    list_parser = subparsers.add_parser(
        "list", help="List students, courses or enrollments."
    )
    list_parser.add_argument(
        "what", choices=["students", "courses", "enrollments"],
        help="What to list.",
    )
    list_parser.add_argument(
        "--sort", choices=list(service.SORT_OPTIONS), default=None,
        help="Sort by name or code.",
    )

    avg = subparsers.add_parser("avg", help="Show a student's average in a course.")
    avg.add_argument("--student-id", required=True, help="Student id.")
    avg.add_argument("--course", required=True, help="Course code.")

    gpa = subparsers.add_parser("gpa", help="Show a student's GPA (0-100 scale).")
    gpa.add_argument("--student-id", required=True, help="Student id.")

    return parser


def handle_add_student(args, data):
    """Add a student and print the new id. Returns True (data changed)."""
    student_id = service.add_student(data, args.name)
    print(f"Added student {args.name.strip()} with id {student_id}.")
    return True


def handle_add_course(args, data):
    """Add a course. Returns True (data changed)."""
    code = service.add_course(data, args.code, args.title)
    print(f"Added course {code}: {args.title.strip()}.")
    return True


def handle_enroll(args, data):
    """Enroll a student in a course. Returns True (data changed)."""
    enrollment = service.enroll(data, args.student_id, args.course)
    print(
        f"Enrolled student {enrollment.student_id} "
        f"in {enrollment.course_code}."
    )
    return True


def handle_add_grade(args, data):
    """Validate and add a grade. Returns True (data changed)."""
    grade = parse_grade(args.grade)
    student_id = parse_student_id(args.student_id)
    course_code = parse_course_code(args.course)
    service.add_grade(data, student_id, course_code, grade)
    print(f"Added grade {grade:g} for student {student_id} in {course_code}.")
    return True


def handle_list(args, data):
    """Print students, courses or enrollments. Returns False (no change)."""
    list_functions = {
        "students": service.list_students,
        "courses": service.list_courses,
        "enrollments": service.list_enrollments,
    }
    items = list_functions[args.what](data, args.sort)
    if not items:
        print(f"No {args.what} yet.")
        return False
    print(f"{args.what.capitalize()}:")
    for item in items:
        print(f"  {item}")
    return False


def handle_avg(args, data):
    """Print a student's average in one course. Returns False (no change)."""
    student_id = parse_student_id(args.student_id)
    course_code = parse_course_code(args.course)
    average = service.compute_average(data, student_id, course_code)
    print(f"Average for student {student_id} in {course_code}: {average:.2f}")
    return False


def handle_gpa(args, data):
    """Print a student's GPA. Returns False (no change)."""
    student_id = parse_student_id(args.student_id)
    gpa = service.compute_gpa(data, student_id)
    print(f"GPA for student {student_id}: {gpa:.2f}")
    return False


COMMAND_HANDLERS = {
    "add-student": handle_add_student,
    "add-course": handle_add_course,
    "enroll": handle_enroll,
    "add-grade": handle_add_grade,
    "list": handle_list,
    "avg": handle_avg,
    "gpa": handle_gpa,
}


def main(argv=None):
    """Parse the command line, run the command and return an exit code."""
    args = build_parser().parse_args(argv)
    try:
        data = load_data()
        changed = COMMAND_HANDLERS[args.command](args, data)
        if changed:
            save_data(data)
    except (ValueError, service.GradebookError, StorageError) as error:
        logger.error("Command '%s' failed: %s", args.command, error)
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())