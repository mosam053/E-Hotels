from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__, static_url_path='', )
app.secret_key = 'mysecretkey'

loggedUserName = ""

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

#Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['loginBtn'] == 'LoginCustomer':
            # Get the inputs from the HTML
            username = request.form['username']
            password = request.form['password']

            conn = sqlite3.connect('ehotels_database.db')
            c = conn.cursor()
            d = conn.cursor()

            d.execute('SELECT SSN FROM Customer WHERE username = ? AND password = ?', (username, password))
            ssn = d.fetchone()            
            if ssn:
                session['ssn'] = ssn[0]
                global loggedSSN
                loggedSSN = ssn

            #SQL Select to see if the user credentials match a row in the database

            c.execute('SELECT * FROM Customer WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            

            if user:
                session['username'] = user[1]
                global loggedUserName
                loggedUserName = username
                conn.close()
                return redirect(url_for('loginCustomerPage', username=username))
            else:
                conn.close()
                return 'Invalid username or password'
        
        elif request.form['loginBtn'] == 'LoginEmployee':
            # TODO: Need to implement username & password validation for employee here, 
            # might need to hard-code some values in the Employee table when we do SQL insertions.
            
            # Get the inputs from the HTML
            username = request.form['username']
            password = request.form['password']

            conn = sqlite3.connect('ehotels_database.db')
            c = conn.cursor()
            d = conn.cursor()
            d.execute('SELECT hotelID from Employee WHERE username = ? AND password = ?', (username, password))
            #SQL Select to see if the user credentials match a row in the database
            c.execute('SELECT * FROM Employee WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            hotelID = d.fetchone()
            if hotelID:
                session['hotelID'] = hotelID[0]
                global employeehotelID  
                employeehotelID = hotelID
                conn.close()
                return redirect(url_for('loginEmployeePage'))
            if user:
                session['username'] = user[1]
                loggedUserName = username
                conn.close()
                return redirect(url_for('loginEmployeePage', username=username))
            else:
                conn.close()
                return 'Invalid username or password'
        
        else:
            return render_template('login.html')
    return render_template('login.html')

#Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the inputs from the HTML
        ssnValue = request.form['SSN']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        street = request.form['street']
        city = request.form['city']
        province = request.form['province']
        zip = request.form['zip']
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('ehotels_database.db')
        c = conn.cursor()

        # SQL insertion statement to create a Customer row
        c.execute('INSERT INTO Customer (SSN, first_name, last_name, street, city, province, zip, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (ssnValue, first_name, last_name, street, city, province, zip, username, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

#Route for the employee page (when they are logged in)
@app.route('/loginEmployeePage', methods=['GET', 'POST'])
def loginEmployeePage():
        
    conn = sqlite3.connect('ehotels_database.db')
    d = conn.cursor()
    d.execute('SELECT * FROM Rooms WHERE Rooms.hotelID = ? AND Rooms.status IS NULL', employeehotelID)
    availableRooms = d.fetchall()

    if request.method == 'POST':
        if request.form['submitBtn'] == 'book-button':
            roomID = request.form['roomID']
            checkinDate = request.form['checkin']
            checkoutDate = request.form['checkout']
            customerSSN = request.form['customerSSN']

            bookingID = customerSSN  + roomID
            bookingDate = checkinDate + " - " + checkoutDate

            createBooking(bookingID, bookingDate, roomID, customerSSN)
            return render_template('employeePage.html', results = availableRooms, hotelName = getHotelName(employeehotelID), rows=getbookingsConfirmation())

    # Render new UI with the selected hotel chain and the associated hotels
    return render_template('employeePage.html', results = availableRooms, hotelName = getHotelName(employeehotelID), rows=getbookingsConfirmation())

def createBooking(bookingID, bookingDate, roomID, SSN):
    ## Create the Booking row
    conn = sqlite3.connect('ehotels_database.db')
    c = conn.cursor()
    c.execute('INSERT INTO Bookings (bookingID, bookingDate, roomID, SSN) VALUES (?, ?, ?, ?)',
                  (bookingID, bookingDate, roomID, SSN))
    c.close()

    ## Set the Room status to "Booked"
    d = conn.cursor()
    d.execute('UPDATE Rooms SET status = "Booked" WHERE roomID=?', (roomID,))

    conn.commit()
    conn.close()
    print((bookingID, bookingDate, roomID, SSN))



# Function for obtaining a list of all the HotelChains stored in the database.
def get_hotel_chains():
    conn = sqlite3.connect('ehotels_database.db')
    c = conn.cursor()
    c.execute('SELECT chainName FROM HotelChain WHERE chainName IS NOT NULL;')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

# Function for obtaining a list of Hotels associated with an input HotelChain.
def get_hotels(chainName):
    conn = sqlite3.connect('ehotels_database.db')
    c = conn.cursor()
    c.execute('SELECT Hotels.locationName, Hotels.hotelID FROM HotelChain INNER JOIN Hotels ON HotelChain.chainName = Hotels.chainName WHERE Hotels.chainName = ?', 
              (chainName,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows
# Function for obtaining a list of Rooms for the employees page

def get_rooms_Employees(employeehotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType):
    print(employeehotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType)

    if(hasWifi == None):
        hasWifi = 0
    if(hasJacuzzi == None):
        hasJacuzzi = 0

     # Connect to the database
    conn = sqlite3.connect('ehotels_database.db')
    d = conn.cursor()
    

    # Execute the SQL query
    sql_query = '''SELECT roomID, hotelID, price, hasWifi, hasJaccuzi, roomCapacity, viewType, extendable
    FROM Rooms
    WHERE hotelID = ?
    AND price BETWEEN ? AND ?
    AND hasWifi = ?
    AND hasJaccuzi = ?
    AND viewType = ?
    AND roomCapacity = ?'''

    d.execute(sql_query, (employeehotelID, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType, numRooms))
    # Fetch the results
    rows = d.fetchall()
    print(rows)
    conn.close()
    return rows
# Function for obtaining a list of Rooms associated with input criteria
def get_rooms(hotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType):

    if(hasWifi == None):
        hasWifi = 0
    if(hasJacuzzi == None):
        hasJacuzzi = 0

    print(hotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType)

     # Connect to the database
    conn = sqlite3.connect('ehotels_database.db')
    cur = conn.cursor()

    # Execute the SQL query
    sql_query = '''SELECT roomID, hotelID, price, hasWifi, hasJaccuzi, roomCapacity, viewType, extendable
    FROM Rooms
    WHERE hotelID = ?
    AND price BETWEEN ? AND ?
    AND hasWifi = ?
    AND hasJaccuzi = ?
    AND viewType = ?
    AND roomCapacity = ?'''

    cur.execute(sql_query, (hotelID, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType, numRooms))
    # Fetch the results
    rows = cur.fetchall()

    conn.close()
    return rows



def get_bookings(username):
    # Connect to the database
    conn = sqlite3.connect('ehotels_database.db')
    cur = conn.cursor()

    cur.execute('''SELECT SSN FROM Customer WHERE username = ?''', (username,))
    ssn = cur.fetchone()[0]

    sql_query = '''SELECT bookingID, bookingDate, roomID 
                   FROM Bookings
                   WHERE SSN = ?'''
    cur.execute(sql_query, (ssn,))

    rows = cur.fetchall()

    conn.close()

    return [(row[2], row[0], row[1]) for row in rows]

#Route for the customer page (when they are logged in)
@app.route('/loginCustomerPage', methods=['GET', 'POST'])
def loginCustomerPage():
    if request.method == 'GET' and ('hotel-chain-filter' or 'hotel-filter' or 'num-rooms-filter' or 'min-price' or 'max-price' or 'hasWifi-filter' or 'hasJacuzzi-filter' or 'viewType-filter') in request.args:
        # get the value of the 'hotel-chain-filer' parameter
        chainName = request.args.get('hotel-chain-filter')

        # create a new 'chains' list where the previously selected hotel chain is at the front of the list.
        newChains = list(filter(lambda c: c != (chainName,), get_hotel_chains()))
        newChains.insert(0, (chainName,))

        # Obtain all other filter attributes
        hotelID = request.args.get('hotel-filter')
        numRooms = request.args.get('num-rooms-filter')
        minPrice = request.args.get('min-price')
        maxPrice = request.args.get('max-price')
        hasWifi = request.args.get('hasWifi-filter')
        hasJacuzzi = request.args.get('hasJacuzzi-filter')
        viewType = request.args.get('viewType-filter')

        bookings = get_bookings(loggedUserName)

        print(get_rooms(hotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType))

        # Render new UI with the selected hotel chain and the associated hotels
        return render_template('customerPage.html', chains = newChains, hotels = get_hotels(chainName), results = get_rooms(hotelID, numRooms, minPrice, maxPrice, hasWifi, hasJacuzzi, viewType), inputChain = chainName, inputCapacity = numRooms, inputMin = minPrice, inputMax = maxPrice, inputWifi = hasWifi, inputJacuzzi = hasJacuzzi, inputView = viewType, bookings=bookings)
    if request.method == 'POST':
        bookingID = request.form['bookingID']
        roomID = request.form['roomID']
        bookingDate = request.form['bookingDate']
        conn = sqlite3.connect('ehotels_database.db')
        try:
            d = conn.cursor()
            ssnValue = loggedSSN[0]
            d.execute('INSERT INTO Bookings (bookingID, roomID, bookingDate, SSN) VALUES (?, ?, ?, ?)',
                (bookingID, roomID, bookingDate, ssnValue))
            conn.commit()
            return redirect(url_for('loginCustomerPage'))
        except Exception as e:
            conn.rollback()
            return "An error occurred: %s" % str(e)

        finally:
            conn.close()
    bookings = get_bookings(loggedUserName)
    return render_template('customerPage.html', chains=get_hotel_chains(), hotels = get_hotels("Accor S.A."), results = get_rooms(1, 1, 10, 400, 1, 0, 'Sea view'), bookings=bookings)




def getbookingsConfirmation():
    conn = sqlite3.connect('ehotels_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM Bookings WHERE bookingID IS NOT NULL;')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def getHotelName(hotelID):
    conn = sqlite3.connect('ehotels_database.db')
    c = conn.cursor()
    c.execute('SELECT locationName FROM Hotels WHERE hotelID = ?', hotelID)
    result = c.fetchone()
    c.close()
    conn.close()
    return result[0]


#Route for the SQL View 1 Page
''' The view was already created in the database, SQL query is in: sqlView.sql '''
@app.route('/sqlView1Page', methods=['GET', 'POST'])
def sqlView1Page():
    # Connect to the database
    conn2 = sqlite3.connect('ehotels_database.db')

    # Create a cursor to execute SQL queries
    cur = conn2.cursor()

    # Execute the SQL query to retrieve all cities in the database
    cur.execute("SELECT DISTINCT City FROM VW_AvailableRoomsPerArea ORDER BY City ASC")

    # Fetch the results
    cities = [row[0] for row in cur.fetchall()]

    print(cities)
    # Close the database connection
    conn2.close()

    if request.method == 'POST':
        # Retrieve the selected city from the form
        selected_city = request.form['city']

        # Connect to the database
        conn = sqlite3.connect('ehotels_database.db')

        # Create a cursor to execute SQL queries
        cur = conn.cursor()

        # Execute the SQL query to retrieve the available rooms for the selected city
        cur.execute("SELECT * FROM VW_AvailableRoomsPerArea WHERE City=?", (selected_city,))

        # Fetch the results
        results = cur.fetchall()

        print(results)

        # Close the database connection
        conn.close()

        # Render the template with the query results
        return render_template('sqlView1Page.html', cities=cities, results=results)

    else:
        # Render the template with the list of cities
        return render_template('sqlView1Page.html', cities=cities)

#Route for the SQL View 2 Page
@app.route('/sqlView2Page', methods=['GET', 'POST'])
def sqlView2Page():
        # Connect to the database
    conn2 = sqlite3.connect('ehotels_database.db')

    # Get a cursor object
    cursor = conn2.cursor()

    # Execute the query to get location names from the Hotels table
    cursor.execute("SELECT locationName FROM Hotels")

    # Fetch all the results into a list
    locations = [row[0] for row in cursor.fetchall()]

    # Close the database connection
    conn2.close()
    
    if request.method == 'POST':
        # Connect to SQLite database
        conn = sqlite3.connect('ehotels_database.db')
        c = conn.cursor()

        # Retrieve the hotel name input from the form
        hotel_name = request.form['hotel_name']
        
        # retrieve the room capacity data for the specified hotel from the view
        cursor = conn.execute('''
        SELECT locationName, roomID, roomCapacity
        FROM VW_RoomCapacity
        WHERE locationName = ?
        ''', (hotel_name,))
        rows = cursor.fetchall()

        return render_template('sqlView2Page.html', rows=rows, locations=locations)
    else:
        return render_template('sqlView2Page.html', locations=locations)


#Route for the user profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global loggedUserName
    print(loggedUserName)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        street = request.form['street']
        city = request.form['city']
        province = request.form['province']

        conn = sqlite3.connect('ehotels_database.db')
    
        cursor = conn.cursor()
        cursor.execute('UPDATE Customer SET first_name=?, last_name=?, street=?, city=?, province=? WHERE username=?',
                       (first_name, last_name, street, city, province, loggedUserName))

        conn.commit()
        return redirect(url_for('profile'))

    else:
        conn = sqlite3.connect('ehotels_database.db')

        cursor = conn.cursor()
        cursor.execute('SELECT first_name, last_name, street, city, province FROM Customer WHERE username=?', (loggedUserName,))
        customer = cursor.fetchone()

        return render_template('profile.html', customer=customer)


if __name__ == '__main__':
    app.run(debug=True)