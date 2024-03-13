import time

def show_course(conn):
    cur=conn.cursor()
    cur.execute('SELECT number, title, room FROM course')
    body = """
    <h2>Student List</h2>
    <p>
    <table border=1>
      <tr>
        <td><font size=+1"><b>number</b></font></td>
        <td><font size=+1"><b>title</b></font></td>
        <td><font size=+1"><b>room</b></font></td>
      </tr>
    """
    
    count = 0
    # each iteration of this loop creates on row of output:
    for number, title, room in cur:
        body += (
            "<tr>"
            f"<td>{number}</td>"
            f"<td><a href='?idNum={number}'>{title}</a></td>"
            f"<td><a href='?idNum={number}'>{room}</a></td>"
            "<td><form method='post' action='university.py'>"
            f"<input type='hidden' NAME='title' VALUE='{title}'>"
            '<input type="submit" name="deleteCourse" value="Delete">'
            "</form></td>"
            "</tr>\n"
        )
        count += 1

    body += "</table>" f"<p>Found {count} courses.</p>"
    
    return body

def showCoursePage(conn, number):
    body = """
    <a href="./university.py">Return to main page.</a>
    """

    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM course
    WHERE number=%s
    """
    cursor.execute(sql, (int(number),))

    data = cursor.fetchall()

    # show profile information
    number, title, room = data[0]

    body += """
    <h2>%s's Course Page</h2>
    <p>
    <table border=1>
        <tr>
            <td>Number</td>
            <td>%s</td>
        </tr>
        <tr>
            <td>Title</td>
            <td>%s</td>
        </tr>
        <tr>
            <td>Room</td>
            <td>%s</td>
        </tr>
    </table>
    """ % (
        number, number, title, room
    )

    # provide an update button:
    body += (
        """
    <FORM METHOD="POST" action="university.py">
    <INPUT TYPE="HIDDEN" NAME="number" VALUE="%s">
    <INPUT TYPE="SUBMIT" NAME="showUpdateCourseForm" VALUE="Update Course">
    </FORM>
    """
        % number
    )

    return body

def deleteCourse(conn, number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM course WHERE number = %s", (number,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Course Succeeded."
    else:
        return "Delete Course Failed."
    
    
def addCourse(conn, number, title, room):
    cursor = conn.cursor()

    sql = "INSERT INTO course VALUES (%s,%s,%s)"
    params = (number, title, room)

    cursor.execute(sql, params)
    conn.commit()

    body = ""
    if cursor.rowcount > 0:
        body = "Added Course "+number
    else:
        body = "Add Course Failed."

    return body, number


def showAddCourseForm():
    return """
    <h2>Add A Course</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Full Number</td>
            <td><INPUT TYPE="TEXT" NAME="number" VALUE=""></td>
        </tr>
        <tr>
            <td>Title</td>
            <td><INPUT TYPE="TEXT" NAME="title" VALUE=""></td>
        </tr>
        <tr>
            <td>Room </td>
            <td><INPUT TYPE="TEXT" NAME="room" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addCourse" value="Add!">
            </td>
        </tr>
    </table>
    </FORM>
    """
    

def getUpdateCourseForm(conn, number, title, room):
    # First, get current data for this student
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM course
    WHERE number=%s
    """
    cursor.execute(sql, (number, title, room))

    data = cursor.fetchall()

    # Create a form to update this student
    (number, title, room) = data[0]

    return """
    <h2>Update Your Course Page</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Course Number</td>
            <td><INPUT TYPE="TEXT" NAME="number" VALUE="%s"></td>
        </tr>
        <tr>
            <td>Title</td>
            <td><INPUT TYPE="TEXT" NAME="title" VALUE="%s"></td>
        </tr>
        <tr>
            <td>Room</td>
            <td><INPUT TYPE="TEXT" NAME="room" VALUE="%s"></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="hidden" name="number" value="%s">
            <input type="submit" name="completeCourseUpdate" value="Update!">
            </td>
        </tr>
    </table>
    </FORM>
    """ % (
        number,
        title,
        room
    )
    

def processCourseUpdate(conn, number, title, room):
    cursor = conn.cursor()

    sql = "UPDATE course SET title=%s, room = %s WHERE number = %s"
    params = (title, room, number)

    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Update Course Succeeded."
    else:
        return "Update Course Failed."

def updateStatusCourseMessage(conn, number, message):
    cursor = conn.cursor()

    tm = time.localtime()
    nowtime = "%04d-%02d-%02d %02d:%02d:%02d" % tm[0:6]

    sql = "INSERT INTO status(profile_id, message, dateTime) VALUES (%s,%s,%s)"
    params = (number, message, nowtime)
    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Succeeded."
    else:
        return "Failed."





