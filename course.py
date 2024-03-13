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

