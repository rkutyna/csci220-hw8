import psycopg2
def show_room(conn):
    cur=conn.cursor()
    cur.execute('SELECT number, capacity FROM room')
    body = """
    <h2>Room List</h2>
    <p>
    <table border=1>
      <tr>
        <td><font size=+1"><b>number</b></font></td>
        <td><font size=+1"><b>capacity</b></font></td>
      </tr>
    """
    
    count = 0
    # each iteration of this loop creates on row of output:
    for number, capacity in cur:
        body += (
            "<tr>"
            f"<td><a href='?roomNum={number}'>{number}</a></td>"
            f"<td>{capacity}</td>"
            "<td><form method='post' action='university.py'>"
            f"<input type='hidden' NAME='roomNum' VALUE='{number}'>"
            '<input type="submit" name="deleteRoom" value="Delete">'
            "</form></td>"
            "</tr>\n"
        )
        count += 1

    body += "</table>" f"<p>Found {count} rooms.</p>"
    
    return body


def showRoomPage(conn, roomNum):
    body = """
    <a href="./university.py">Return to main page.</a>
    """
    cursor = conn.cursor()
    print(roomNum)
    sql = """
    SELECT *
    FROM room
    WHERE number=%s
    """
    cursor.execute(sql, (str(roomNum),))

    data = cursor.fetchall()

    # show profile information
    roomNum, capacity = data[0]

    body += """
    <h2>%s</h2>
    <p>
    <table border=1>
        <tr>
            <td>room</td>
            <td>%s</td>
        </tr>
        <tr>
            <td>capacity</td>
            <td>%s</td>
        </tr>
    </table>
    """ % (
        roomNum, roomNum, capacity
    )

    # provide an update button:
    body += (
        """
    <FORM METHOD="POST" action="university.py">
    <INPUT TYPE="HIDDEN" NAME="roomNum" VALUE="%s">
    <INPUT TYPE="SUBMIT" NAME="showUpdateRoomForm" VALUE="Update room">
    </FORM>
    """
        % roomNum
    )

    return body


def deleteRoom(conn, roomNum):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM room WHERE number = %s", (roomNum,))
    conn.commit()
    if cursor.rowcount > 0:
        return "Delete Room Succeeded."
    else:
        return "Delete Room Failed."
    
    

def addRoom(conn, number, capacity):
    cursor = conn.cursor()

    #check for existing room number
    check = "SELECT number FROM room WHERE number = %s"
    #insert a new room
    insert = "INSERT INTO room (number, capacity) VALUES (%s, %s)"
    
    try:
        # Check if the room number already exists
        cursor.execute(check, (number,))
        if cursor.fetchone() is not None:
            return "Error: A room with this number already exists.", number

        # If it does not exist, add the new room
        cursor.execute(insert, (number, capacity))
        conn.commit()
        return "Added room " + number, number

    except psycopg2.Error as e:
        # Catch any other PostgreSQL errors
        print("Database error:", e)
        return "Add room Failed.", number

def showAddRoomForm():
    return """
    <h2>Add A Room</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Room Number</td>
            <td><INPUT TYPE="TEXT" NAME="roomNum" VALUE=""></td>
        </tr>
        <tr>
            <td>Room Capacity</td>
            <td><INPUT TYPE="TEXT" NAME="capacity" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="submit" name="addRoom" value="Add!">
            </td>
        </tr>
    </table>
    </FORM>
    """
    
    
def getUpdateRoomForm(conn, roomNum):
    # First, get current data for this student
    cursor = conn.cursor()

    sql = """
    SELECT *
    FROM room
    WHERE number=%s
    """
    cursor.execute(sql, (roomNum,))

    data = cursor.fetchall()

    # Create a form to update this student
    (roomNum, capacity) = data[0]

    return """
    <h2>Update %s</h2>
    <p>
    <FORM METHOD="POST">
    <table>
        <tr>
            <td>Room Capacity</td>
            <td><INPUT TYPE="TEXT" NAME="capacity" VALUE=""></td>
        </tr>
        <tr>
            <td></td>
            <td>
            <input type="hidden" name="roomNum" value="%s">
            <input type="submit" name="completeRoomUpdate" value="Update!">
            </td>
        </tr>
    </table>
    </FORM>
    """ % (
        roomNum,
        roomNum
    )
    
def processRoomUpdate(conn, roomNum, capacity):
    print("checkyyyyyy \n \n")
    cursor = conn.cursor()

    sql = "UPDATE room SET capacity=%s WHERE number = %s"
    params = (capacity, roomNum)

    cursor.execute(sql, params)
    conn.commit()

    if cursor.rowcount > 0:
        return "Update Room Succeeded."
    else:
        return "Update Room Failed."