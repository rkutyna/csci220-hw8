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
            f"<td><a href='?idNum={id}'>{id}</a></td>"
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
    
def addProfile(conn, name):
    cursor = conn.cursor()

    sql = "SELECT max(ID) FROM profiles"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        nextID = int(data[0]) + 1
    except:
        nextID = 1

    sql = "INSERT INTO profiles VALUES (%s,%s)"
    params = (nextID, name)

    cursor.execute(sql, params)
    conn.commit()

    body = ""
    if cursor.rowcount > 0:
        body = "Add Profile Succeeded."
    else:
        body = "Add Profile Failed."

    return body, nextID

def getUpdateProfileForm(conn, idNum):
    # First, get current data for this profile
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM profiles
    WHERE id=%s
    """
    cursor.execute(sql, (idNum,))

    data = cursor.fetchall()

    # Create a form to update this profile
    (idNum, name) = data[0]

    return """
    <h2>Update Your Profile Page</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Name</td>
            <td><INPUT TYPE="TEXT" NAME="name" VALUE="%s"></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="hidden" name="idNum" value="%s">
            <input type="submit" name="completeUpdate" value="Update!">
            </td>
        </tr>
    </table>
    </FORM>
    """ % (
        name,
        idNum
    )
    
def processProfileUpdate(conn, idNum, name):
    cursor = conn.cursor()

    sql = "UPDATE profiles SET name=%s, WHERE id = %s"
    params = (name, idNum)

    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Update Profile Succeeded."
    else:
        return "Update Profile Failed."

def updateStatusMessage(conn, idNum, message):
    cursor = conn.cursor()

    tm = time.localtime()
    nowtime = "%04d-%02d-%02d %02d:%02d:%02d" % tm[0:6]

    sql = "INSERT INTO status(profile_id, message, dateTime) VALUES (%s,%s,%s)"
    params = (idNum, message, nowtime)
    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Succeeded."
    else:
        return "Failed."

def showAddProfileForm():
    return """
    <h2>Add A Profile</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Full Name</td>
            <td><INPUT TYPE="TEXT" NAME="name" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addProfile" value="Add!">
            </td>
        </tr>
    </table>
    </FORM>
    """
    



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
        
# Colin solution
        
# def show_enrollments(conn):
#     cursor = conn.cursor()
#     cursor.execute("SELECT c.number as Number, COALESCE(COUNT(e.student), 0) as Enrollment FROM course AS c LEFT OUTER JOIN enrolled AS e ON c.number = e.course GROUP BY c.number")
#     enrollment = cursor.fetchall()
#     print("Number|Enrollment")
#     for row in  enrollment:
#         print(f"{row[0]}|{row[1]}")
#     conn.close()


# def add_student(conn, id, name):
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO student VALUES (?, ?)", (id, name))
#         conn.commit()
#     except sqlite3.IntegrityError:
#         print("UNIQUE constraint failed: student.id")
#     finally:
#         conn.close()

# def enroll_student(conn, student, course):
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO enrolled VALUES (?, ?)", (student, course))
#         conn.commit()
#     except sqlite3.IntegrityError:
#         print("UNIQUE constraint failed: enrolled.student, enrolled.course")
#     finally:
#         conn.close()


# def declare_major(conn, student, department):
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO majors_in (student, dept) VALUES (?, ?)", (student, department))
#         conn.commit()
#     except sqlite3.IntegrityError:
#         print("UNIQUE constraint failed: majors_in.student, majors_in.dept")
#     finally:
        
#         conn.close()


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
