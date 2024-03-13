import argparse
import sqlite3
import sys
import os
import time
from urllib.parse import parse_qs
from html import escape
from course import *

import psycopg2

def wrapBody(body, title="Blank Title"):
    return (
        "<html>\n"
        "<head>\n"
        f"<title>{title}</title>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "<hr>\n"
        f"<p>This page was generated at {time.ctime()}.</p>\n"
        "</body>\n"
        "</html>\n"
    )
    
def show_students(conn):
    cur=conn.cursor()
    cur.execute('SELECT id, name FROM student')
    body = """
    <h2>Student List</h2>
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
            f"<td>{id}</td>"
            f"<td><a href='?idNum={id}'>{name}</a></td>"
            "<td><form method='post' action='university.py'>"
            f"<input type='hidden' NAME='idNum' VALUE='{id}'>"
            '<input type="submit" name="deleteStudent" value="Delete">'
            "</form></td>"
            "</tr>\n"
        )
        count += 1

    body += "</table>" f"<p>Found {count} students.</p>"
    
    return body


def showStudentPage(conn, idNum):
    body = """
    <a href="./university.py">Return to main page.</a>
    """

    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM student
    WHERE id=%s
    """
    cursor.execute(sql, (int(idNum),))

    data = cursor.fetchall()

    # show profile information
    idNum, name = data[0]

    body += """
    <h2>%s's Profile Page</h2>
    <p>
    <table border=1>
        <tr>
            <td>ID</td>
            <td>%s</td>
        </tr>
        <tr>
            <td>Name</td>
            <td>%s</td>
        </tr>
    </table>
    """ % (
        name, idNum, name
    )

    # provide an update button:
    body += (
        """
    <FORM METHOD="POST" action="university.py">
    <INPUT TYPE="HIDDEN" NAME="idNum" VALUE="%s">
    <INPUT TYPE="SUBMIT" NAME="showUpdateStudentForm" VALUE="Update Student">
    </FORM>
    """
        % idNum
    )

    return body


def deleteStudent(conn, idNum):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (idNum,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Student Succeeded."
    else:
        return "Delete Student Failed."
    
    
def addStudent(conn, name):
    cursor = conn.cursor()

    sql = "SELECT max(ID) FROM student"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        nextID = int(data[0]) + 1
    except:
        nextID = 1

    sql = "INSERT INTO student VALUES (%s,%s)"
    params = (nextID, name)

    cursor.execute(sql, params)
    conn.commit()

    body = ""
    if cursor.rowcount > 0:
        body = "Added Student "+name
    else:
        body = "Add Student Failed."

    return body, nextID

def showAddStudentForm():
    return """
    <h2>Add A Student</h2>
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
            <input type="submit" name="addStudent" value="Add!">
            </td>
        </tr>
    </table>
    </FORM>
    """
    
    
def getUpdateStudentForm(conn, idNum):
    # First, get current data for this student
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM student
    WHERE id=%s
    """
    cursor.execute(sql, (idNum,))

    data = cursor.fetchall()

    # Create a form to update this student
    (idNum, name) = data[0]

    return """
    <h2>Update Your Student Page</h2>
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
    
def processStudentUpdate(conn, idNum, name):
    cursor = conn.cursor()

    sql = "UPDATE student SET name=%s WHERE id = %s"
    params = (name, idNum)

    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Update Student Succeeded."
    else:
        return "Update Student Failed."

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
        


def get_qs_post(env):
    """
    :param env: WSGI environment
    :returns: A tuple (qs, post), containing the query string and post data,
              respectively
    """
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(env.get("CONTENT_LENGTH", 0))
    except (ValueError):
        request_body_size = 0
    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = env["wsgi.input"].read(request_body_size).decode("utf-8")
    post = parse_qs(request_body)
    return parse_qs(env["QUERY_STRING"]), post

def application(env, start_response):
    qs, post = get_qs_post(env)

    body = ""
    try:
        conn = psycopg2.connect(
            host="postgres",
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
    except psycopg2.Warning as e:
        print(f"Database warning: {e}")
        body += "Check logs for DB warning"
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        body += "Check logs for DB error"
    
    idNum = None
    if "idNum" in post:
        idNum = post["idNum"][0]
        # handle case of starting to do an update -- show the form
        if "showUpdateStudentForm" in post and "idNum" in post:
            body += getUpdateStudentForm(conn, post["idNum"][0])
        ## handle case of completing an update
        elif "completeUpdate" in post:
            body += processStudentUpdate(
                conn,
                idNum,
                post["name"][0],
            )
        # handle case of showing a student page
        elif "processStatusUpdate" in post:
            messages = post["message"][0]
            body += updateStatusMessage(conn, idNum, messages)
        elif "deleteStudent" in post:
            body += deleteStudent(conn, idNum)
            idNum = None
    # handle case of adding a Student page:
    elif "addStudent" in post:
        b, idNum = addStudent(
            conn,
            post["name"][0]
        )
        body += b
    elif "idNum" in qs:
        idNum = qs.get("idNum")[0]
    if idNum:
        # Finish by showing the student page
        body += showStudentPage(conn, idNum)
    # default case: show all students
    else:
        body += show_students(conn)
        body += showAddStudentForm()
        
    start_response("200 OK", [("Content-Type", "text/html")])
    return [wrapBody(body, title="University").encode("utf-8")]