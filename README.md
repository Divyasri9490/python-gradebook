# Gradebook CLI

A small command-line gradebook written in Python. It lets you add students
and courses, enroll students in courses, record grades, and calculate a
student's course average and GPA. Data is saved to a JSON file and important
events are written to a log file.

The project uses only the Python standard library (no extra packages).

## Features

- Add students (ids are assigned automatically: 1, 2, 3, ...)
- Add courses (course codes are stored in capital letters, e.g. `CS101`)
- Enroll a student in a course
- Add grades from 0 to 100
- List students, courses or enrollments, with optional sorting
- Show a student's average in one course
- Show a student's GPA (simple mean of their course averages)
- Input validation with friendly error messages
- Data saved to `data/gradebook.json`
- INFO and ERROR messages logged to `logs/app.log`
- Sample data script and unit tests

## Project structure

```
gradebook/                  <- project folder (run all commands from here)
├── gradebook/              <- the Python package
│   ├── __init__.py         <- marks the folder as a package
│   ├── logger.py           <- logging setup (writes logs/app.log)
│   ├── models.py           <- Student, Course and Enrollment classes
│   ├── service.py          <- business logic (add, enroll, average, GPA)
│   ├── storage.py          <- load_data() and save_data() for JSON
│   └── validators.py       <- input helpers such as parse_grade()
├── data/
│   └── gradebook.json      <- saved data (created by the program)
├── logs/
│   └── app.log             <- log file (created by the program)
├── scripts/
│   └── seed.py             <- creates sample data
├── tests/
│   ├── __init__.py
│   └── test_service.py     <- unit tests (unittest)
├── main.py                 <- command-line interface (argparse)
├── README.md
└── .gitignore
```

## Requirements

- Python 3.8 or newer
- No extra packages are needed

## Setup

Open a terminal in the project folder.

1. Create a virtual environment (a private copy of Python for this project):

   ```
   python -m venv .venv
   ```

2. Activate it.

   Windows (PowerShell):

   ```
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell says running scripts is disabled, run this first (it only
   affects the current terminal window), then activate again:

   ```
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

   

## Create sample data

```
python scripts/seed.py
```

Expected output:

```
Saved sample data to <your project folder>/data/gradebook.json
3 students, 2 courses, 4 enrollments.
```

Warning: this replaces any existing data in `data/gradebook.json`.

The sample data contains:

| Student          | Course  | Grades     |
|------------------|---------|------------|
| 1 Alice Johnson  | CS101   | 95, 88     |
| 1 Alice Johnson  | MATH201 | 78, 85     |
| 2 Bob Smith      | CS101   | 72, 80, 91 |
| 3 Chitra Rao     | MATH201 | 90, 94     |

## Usage

General form:

```
python main.py <command> [options]
python main.py --help
python main.py <command> --help
```



`list` takes `students`, `courses` or `enrollments`, and an optional
`--sort name` or `--sort code`:

| What          | No `--sort` (default)        | `--sort name`        | `--sort code`               |
|---------------|------------------------------|----------------------|-----------------------------|
| `students`    | by id                        | by name              | by id                       |
| `courses`     | by code                      | by title             | by code                     |
| `enrollments` | by student id, then course   | by student name      | by course code, then student|

### Examples with expected output

These examples assume you have just run `python scripts/seed.py`.

```
> python main.py list students --sort name
Students:
  [1] Alice Johnson
  [2] Bob Smith
  [3] Chitra Rao

> python main.py list courses
Courses:
  CS101: Intro to CS
  MATH201: Linear Algebra

> python main.py list enrollments --sort code
Enrollments:
  Student 1 in CS101 - grades: 95, 88
  Student 2 in CS101 - grades: 72, 80, 91
  Student 1 in MATH201 - grades: 78, 85
  Student 3 in MATH201 - grades: 90, 94

> python main.py avg --student-id 1 --course CS101
Average for student 1 in CS101: 91.50

> python main.py avg --student-id 2 --course CS101
Average for student 2 in CS101: 81.00

> python main.py gpa --student-id 1
GPA for student 1: 86.50

> python main.py add-student --name "Dana Lee"
Added student Dana Lee with id 4.

> python main.py add-course --code PHY101 --title "Physics I"
Added course PHY101: Physics I.

> python main.py enroll --student-id 4 --course PHY101
Enrolled student 4 in PHY101.

> python main.py add-grade --student-id 4 --course PHY101 --grade 87
Added grade 87 for student 4 in PHY101.
```

### Error examples

Errors are shown as a single friendly line (and written to `logs/app.log`):

```
> python main.py add-grade --student-id 1 --course CS101 --grade 150
Error: Grade must be between 0 and 100, got 150.

> python main.py enroll --student-id 99 --course CS101
Error: No student with id 99.

> python main.py avg --student-id 2 --course MATH201
Error: Student 2 is not enrolled in MATH201.
```

## Inspecting the data and log files

Windows (PowerShell):

```
Get-Content data\gradebook.json
Get-Content logs\app.log
```



Example log lines:

```
2026-11-17 11:03:05,460 INFO gradebook: Saved data to ...\data\gradebook.json.
2026-11-17 11:04:20,789 ERROR gradebook: Command 'add-grade' failed: Grade must be between 0 and 100, got 150.
```

## Running the tests

From the project folder, with the virtual environment active:

```
python -m unittest -v
```

Expected result (last lines):

```
Ran 10 tests in 0.004s

OK
```

The tests cover `add_student`, `add_grade`, `compute_average` and
`compute_gpa`, including failing and edge cases (empty name, grades outside
0-100, a student who is not enrolled, an average with no grades). They work
on in-memory data only, so they do not change `data/gradebook.json`.

## Design decisions & limitations

**Design decisions**

- Each file has one job: `models.py` (classes), `validators.py` (input
  checks), `storage.py` (JSON), `service.py` (business logic) and `main.py`
  (command line).
- Service functions take the data as their first argument, e.g.
  `add_student(data, name)` instead of `add_student(name)`. They never touch
  files, so tests can use in-memory data. `main.py` loads, calls the
  function and saves only if something changed.
- A missing data file starts an empty gradebook. A damaged file shows a
  clear error message and is not overwritten.
- GPA is the simple mean of course averages on the 0-100 scale. Courses
  with no grades are skipped.

**Limitations**

- There are no commands to edit or delete data.
- The whole JSON file is rewritten on every change, and there is no
  protection against two people using it at the same time.
- `scripts/seed.py` replaces all existing data.