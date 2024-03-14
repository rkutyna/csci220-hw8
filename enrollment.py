import argparse
import sqlite3
import sys
import os
import time
from urllib.parse import parse_qs
from html import escape
from course import *
import psycopg2
from university import *

def show_enrolled(conn):
    cur=conn.cursor()
    cur.execute('SELECT number, COUNT(student) FROM course LEFT JOIN enrolled ON enrolled.course = course.number GROUP BY number')
    body = """
    <h2>List of Enrollment Numbers</h2>
    <p>
    <table border=1>
      <tr>
        <td><font size=+1"><b>number</b></font></td>
        <td><font size=+1"><b>enrolled</b></font></td>
      </tr>
    """
    
    count = 0
    # each iteration of this loop creates on row of output:
    for number, count in cur:
        body += (
            "<tr>"
            f"<td>{number}</td>"
            f"<td><a href='?cnumber={number}'>{count}</a></td>"
            "</tr>\n"
        )
    
    body += "</table>"
    body += showAddEnrollmentForm()  # Add the enrollment form after the table
    return body

def showEnrolledPage(conn, number):
    body = """
    <a href="./university.py">Return to main page.</a>
    """

    cursor = conn.cursor()

    sql = """
    SELECT name, student FROM enrolled JOIN student ON student.id=enrolled.student WHERE course =%s
    """
    cursor.execute(sql,(str(number),))

    data = cursor.fetchall()

    # show profile information

    body += """
    <h2>Students enrolled in %s</h2>
    <p>
    <table border=1>
        <tr>
            <td>room</td>
        <td>""" % (number)
    for name, id in data:
        body+=(
            "<tr>"
            f"<td>{name}</td>"
            "<td><form method='post' action='university.py'>"
            f"<input type='hidden' NAME='cnumber' VALUE='{number}'>"
            f"<input type='hidden' NAME='id' VALUE='{id}'>"
            '<input type="submit" name="deleteEnrolled" value="Delete">'
            "</form></td>"
            "</tr>\n"
        )
    body+="""
    </tr>
    </table>
    """ 

    # provide an update button:
    

    return body

def deleteEnrolled(conn, id, number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM enrolled WHERE student = %s AND course = %s", (id,number,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Enrollment Succeeded."
    else:
        return "Delete Enrollment Failed."
    
    
def addEnrolled(conn, number, id):
    print("added enrollement")
    cursor = conn.cursor()

    sql = "INSERT INTO enrolled VALUES (%s,%s)"
    params = (id, number)

    cursor.execute(sql, params)
    conn.commit()

    body = ""
    if cursor.rowcount > 0:
        body = "Added Student #"+ str(id)+" To Course "+ number
    else:
        body = "Add Enrollment Failed."

    return body, number


def showAddEnrollmentForm():
    return """
    <h2>Add An Enrollment</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Student ID</td>
            <td><INPUT TYPE="TEXT" NAME="id" VALUE=""></td>
        </tr>
        <tr>
            <td>Course Number</td>
            <td><INPUT TYPE="TEXT" NAME="cnumber" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addEnrollment" value="Add!">
            </td>
        </tr>
    </table>
    </FORM>
    """
    

def getUpdateCourseForm(conn, number):
    # First, get current data for this student
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM course
    WHERE number=%s
    """
    cursor.execute(sql, (str(number),))

    data = cursor.fetchall()

    # Create a form to update this student
    (number, title, room) = data[0]

    return """
    <h2>Update Course %s</h2>
    <p>
    <FORM METHOD="POST">
    <table>
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
        room,
        number
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
