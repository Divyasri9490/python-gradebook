"""Unit tests for gradebook.service.

Run from the project folder with:
    python -m unittest -v
"""

import unittest

from gradebook import service
from gradebook.storage import empty_data


class AddStudentTests(unittest.TestCase):
    """Tests for service.add_student."""

    def setUp(self):
        """Start every test with a new, empty gradebook."""
        self.data = empty_data()

    def test_add_student_returns_increasing_ids(self):
        """Happy path: ids start at 1 and go up by one."""
        first_id = service.add_student(self.data, "Alice")
        second_id = service.add_student(self.data, "Bob")
        self.assertEqual(first_id, 1)
        self.assertEqual(second_id, 2)
        names = [student.name for student in self.data["students"]]
        self.assertEqual(names, ["Alice", "Bob"])

    def test_add_student_strips_extra_spaces(self):
        """Edge case: spaces around the name are removed."""
        student_id = service.add_student(self.data, "  Alice  ")
        student = service.find_student(self.data, student_id)
        self.assertEqual(student.name, "Alice")

    def test_add_student_with_empty_name_raises(self):
        """Failing case: an empty name raises ValueError and adds nothing."""
        with self.assertRaises(ValueError):
            service.add_student(self.data, "   ")
        self.assertEqual(self.data["students"], [])


class GradeTests(unittest.TestCase):
    """Tests for service.add_grade, compute_average and compute_gpa."""

    def setUp(self):
        """Create one student enrolled in CS101 before every test."""
        self.data = empty_data()
        self.student_id = service.add_student(self.data, "Alice")
        service.add_course(self.data, "CS101", "Intro to CS")
        service.enroll(self.data, self.student_id, "CS101")

    def get_grades(self, course_code="CS101"):
        """Return the stored grades of the test student in a course."""
        enrollment = service.find_enrollment(
            self.data, self.student_id, course_code
        )
        return enrollment.grades

    def test_add_grade_stores_grade(self):
        """Happy path: a text grade like '95' is stored as 95.0."""
        result = service.add_grade(self.data, self.student_id, "CS101", "95")
        self.assertEqual(result, 95.0)
        self.assertEqual(self.get_grades(), [95.0])

    def test_add_grade_accepts_boundary_values(self):
        """Edge case: 0 and 100 are both valid grades."""
        service.add_grade(self.data, self.student_id, "CS101", 0)
        service.add_grade(self.data, self.student_id, "CS101", 100)
        self.assertEqual(self.get_grades(), [0.0, 100.0])

    def test_add_grade_invalid_value_raises(self):
        """Failing case: grades outside 0-100 or not numbers are rejected."""
        for bad_grade in (-1, 101, "abc"):
            with self.subTest(grade=bad_grade):
                with self.assertRaises(ValueError):
                    service.add_grade(
                        self.data, self.student_id, "CS101", bad_grade
                    )
        self.assertEqual(self.get_grades(), [])

    def test_add_grade_for_unenrolled_student_raises(self):
        """Failing case: a student not enrolled in the course is rejected."""
        other_id = service.add_student(self.data, "Bob")
        with self.assertRaises(service.GradebookError):
            service.add_grade(self.data, other_id, "CS101", 80)

    def test_compute_average(self):
        """Happy path: the average is the mean of the grades."""
        for grade in (90, 85, 100):
            service.add_grade(self.data, self.student_id, "CS101", grade)
        average = service.compute_average(self.data, self.student_id, "CS101")
        self.assertAlmostEqual(average, 91.67, places=2)

    def test_compute_average_without_grades_raises(self):
        """Edge case: an average with no grades raises GradebookError."""
        with self.assertRaises(service.GradebookError):
            service.compute_average(self.data, self.student_id, "CS101")

    def test_compute_gpa_is_mean_of_course_averages(self):
        """Happy path: GPA is the simple mean of course averages."""
        service.add_course(self.data, "MATH201", "Linear Algebra")
        service.enroll(self.data, self.student_id, "MATH201")
        service.add_grade(self.data, self.student_id, "CS101", 90)
        service.add_grade(self.data, self.student_id, "CS101", 80)
        service.add_grade(self.data, self.student_id, "MATH201", 70)
        gpa = service.compute_gpa(self.data, self.student_id)
        self.assertAlmostEqual(gpa, 77.5)


if __name__ == "__main__":
    unittest.main()