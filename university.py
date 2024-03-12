import argparse
import sqlite3
import sys


def show_students(conn):
    cur=conn.cursor()
    cur.execute('SELECT id, name FROM student')
    body = """
    <h2>Profile List</h2>
    <p>
    <table border=1>
      <tr>
        <td><font size=+1"><b>id</b></font></td>
        <td><font size=+1"><b>name</b></font></td>
      </tr>
    """
    
    count = 0
    # each iteration of this loop creates on row of output:
    for id, name in cur:
        body += (
            "<tr>"
            f"<td><a href='?idNum={id}'>{name}</a></td>"
            "<td><form method='post' action='university.py'>"
            f"<input type='hidden' NAME='idNum' VALUE='{id}'>"
            '<input type="submit" name="deleteProfile" value="Delete">'
            "</form></td>"
            "</tr>\n"
        )
        count += 1

    body += "</table>" f"<p>Found {count} profiles.</p>"
    
    return body
    
def deleteProfile(conn, idNum):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (idNum,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Profile Succeeded."
    else:
        return "Delete Profile Failed."


def show_enrollments(conn):
    try:
        cur=conn.cursor()
        cur.execute('SELECT number, COUNT(student) FROM course LEFT JOIN enrolled ON enrolled.course = course.number GROUP BY number')
        print(f'Number|Enrollment')
        for row in cur:
            number, total = row
            print(f'{number}|{total}')
    except Exception as e:
        print(e)
        

def add_student(conn, id, name):
    try:
        cur=conn.cursor()
        cur.execute('INSERT INTO student VALUES (?,?)', (id, name))
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(str(e) + '\n')


def enroll_student(conn, student, course):
    try:
        cur=conn.cursor()
        cur.execute('INSERT INTO enrolled VALUES (?,?)', (student, course))
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(str(e) + '\n')


def declare_major(conn, student, department):
    try:
        cur=conn.cursor()
        cur.execute('INSERT INTO majors_in VALUES (?,?)', (student, department))
        conn.commit()
    except sqlite3.IntegrityError as e:
        sys.stderr.write(str(e) + '\n')


def main():
    argparser = argparse.ArgumentParser(
        description="Interact with the university database"
    )
    argparser.add_argument(
        "database",
        help="SQLite database file",
    )
    argparser.add_argument(
        "--add-student",
        metavar=("ID", "NAME"),
        nargs=2,
        help="Add a student",
    )
    argparser.add_argument(
        "--enroll-student",
        metavar=("STUDENT", "COURSE"),
        nargs=2,
        help="Enroll a student in a course",
    )
    argparser.add_argument(
        "--declare-major",
        metavar=("STUDENT", "DEPARTMENT"),
        nargs=2,
        help="Declare a student's major",
    )
    argparser.add_argument(
        "--show-students",
        action="store_true",
        help="List all students IDs, names, and their majors",
    )
    argparser.add_argument(
        "--show-enrollments",
        action="store_true",
        help="List all courses and the number of students enrolled",
    )
    args = argparser.parse_args()
    conn = sqlite3.connect(args.database)
    conn.execute("PRAGMA foreign_keys = ON")
    if args.add_student:
        add_student(conn, *args.add_student)
    if args.enroll_student:
        enroll_student(conn, *args.enroll_student)
    if args.declare_major:
        declare_major(conn, *args.declare_major)
    if args.show_students:
        show_students(conn)
    if args.show_enrollments:
        show_enrollments(conn)


if __name__ == "__main__":
    main()
