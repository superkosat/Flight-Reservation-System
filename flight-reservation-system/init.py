from flask import Flask, render_template, session, request, url_for, redirect, flash, abort, make_response
import pymysql.cursors
from datetime import date

app = Flask(__name__)

#Establish connection to MySQL server
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='flight_reservation_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

### context processors and macro functions ###

def is_logged_in():
    return 'username' in session

@app.context_processor
def inject_user():
    return dict(is_logged_in=is_logged_in)



### Define routes ###

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    return

#route to query database for flights from home page regardless of user status
@app.route('/searchFlights', methods=['GET', 'POST'])
def searchFlights():
    departureCity = request.form['departureCity']
    arrivalCity = request.form['arrivalCity']
    departureAirport = request.form['departureAirport']
    arrivalAirport = request.form['arrivalAirport']
    flightDate = request.form['flightDate']

    conditions = []
    params = []

    if departureCity:
        conditions.append("a.airport_city = %s")
        params.append(departureCity)
    if arrivalCity:
        conditions.append("b.airport_city = %s")
        params.append(arrivalCity)
    if departureAirport:
        conditions.append("flight.departure_airport = %s")
        params.append(departureAirport)
    if arrivalAirport:
        conditions.append("flight.arrival_airport = %s")
        params.append(arrivalAirport)
    if flightDate:
        start_date = flightDate + " 00:00:00"
        end_date = flightDate + " 23:59:59"
        conditions.append("flight.departure_time BETWEEN %s AND %s")
        params.extend([start_date, end_date])

    error = None

    if not any([departureCity, arrivalCity, departureAirport, arrivalAirport, flightDate]):
        error = "Please fill at least one field"
        return render_template('home.html', error=error)

    cursor = conn.cursor()


    query = '''
        SELECT flight.*, a.airport_city AS departure_city, b.airport_city AS arrival_city
        FROM flight 
        INNER JOIN airport AS a ON flight.departure_airport = a.airport_name 
        INNER JOIN airport AS b ON flight.arrival_airport = b.airport_name 
        WHERE {}
    '''.format(" AND ".join(conditions))

    cursor.execute(query, params)

    data = cursor.fetchall()

    cursor.close()

    if data:
        return render_template('search_display.html', data=data)
    else:
        error = 'No flights found'
        return render_template('search_display.html', error=error)

#route for user login, renders login template
@app.route('/login')
def login():
    return render_template('login.html')

#route for user logout, destroys session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#route for login authentication
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    #SELECT * FROM customer WHERE email = %s AND password = %s
    cursor = conn.cursor()
    query = '''
        SELECT 'customer' AS user_type, email, password, name FROM customer WHERE email = %s AND password = %s
        UNION
        SELECT 'airline_staff' AS user_type, username AS email, password, first_name FROM airline_staff WHERE username = %s AND password = %s
        UNION
        SELECT 'booking_agent' AS user_type, email, password, booking_agent_id FROM booking_agent WHERE email = %s AND password = %s
    '''
    cursor.execute(query, (username, password, username, password, username, password))

    data = cursor.fetchone()

    error = None
    if (data):
        session['username'] = username
        session['user_type'] = data['user_type']
        session['name'] = data['name']
        if session['user_type'] == 'airline_staff':
            query = "SELECT permission_type FROM permission INNER JOIN airline_staff ON airline_staff.username = permission.username WHERE airline_staff.username = %s"
            cursor.execute(query, (username))
            data = cursor.fetchone()
            session['permission'] = data['permission_type']
        cursor.close()
        return redirect(url_for('home'))
    else:
        cursor.close()
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

#route to render the new user registration template
@app.route('/register')
def register():
    states = [
    {"abbr": "AL", "name": "Alabama"},
    {"abbr": "AK", "name": "Alaska"},
    {"abbr": "AZ", "name": "Arizona"},
    {"abbr": "AR", "name": "Arkansas"},
    {"abbr": "CA", "name": "California"},
    {"abbr": "CO", "name": "Colorado"},
    {"abbr": "CT", "name": "Connecticut"},
    {"abbr": "DE", "name": "Delaware"},
    {"abbr": "FL", "name": "Florida"},
    {"abbr": "GA", "name": "Georgia"},
    {"abbr": "HI", "name": "Hawaii"},
    {"abbr": "ID", "name": "Idaho"},
    {"abbr": "IL", "name": "Illinois"},
    {"abbr": "IN", "name": "Indiana"},
    {"abbr": "IA", "name": "Iowa"},
    {"abbr": "KS", "name": "Kansas"},
    {"abbr": "KY", "name": "Kentucky"},
    {"abbr": "LA", "name": "Louisiana"},
    {"abbr": "ME", "name": "Maine"},
    {"abbr": "MD", "name": "Maryland"},
    {"abbr": "MA", "name": "Massachusetts"},
    {"abbr": "MI", "name": "Michigan"},
    {"abbr": "MN", "name": "Minnesota"},
    {"abbr": "MS", "name": "Mississippi"},
    {"abbr": "MO", "name": "Missouri"},
    {"abbr": "MT", "name": "Montana"},
    {"abbr": "NE", "name": "Nebraska"},
    {"abbr": "NV", "name": "Nevada"},
    {"abbr": "NH", "name": "New Hampshire"},
    {"abbr": "NJ", "name": "New Jersey"},
    {"abbr": "NM", "name": "New Mexico"},
    {"abbr": "NY", "name": "New York"},
    {"abbr": "NC", "name": "North Carolina"},
    {"abbr": "ND", "name": "North Dakota"},
    {"abbr": "OH", "name": "Ohio"},
    {"abbr": "OK", "name": "Oklahoma"},
    {"abbr": "OR", "name": "Oregon"},
    {"abbr": "PA", "name": "Pennsylvania"},
    {"abbr": "RI", "name": "Rhode Island"},
    {"abbr": "SC", "name": "South Carolina"},
    {"abbr": "SD", "name": "South Dakota"},
    {"abbr": "TN", "name": "Tennessee"},
    {"abbr": "TX", "name": "Texas"},
    {"abbr": "UT", "name": "Utah"},
    {"abbr": "VT", "name": "Vermont"},
    {"abbr": "VA", "name": "Virginia"},
    {"abbr": "WA", "name": "Washington"},
    {"abbr": "WV", "name": "West Virginia"},
    {"abbr": "WI", "name": "Wisconsin"},
    {"abbr": "WY", "name": "Wyoming"},
    {"abbr": "PR", "name": "Puerto Rico"},
    {"abbr": "GU", "name": "Guam"}
    ]

    cursor = conn.cursor()
    query = 'SELECT * FROM airline;'
    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()

    return render_template('register.html', states=states, data=data)

#route to insert new customer user into database
@app.route('/registerCustomer', methods=['GET', 'POST'])
def registerCustomer():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    buildingNumber = request.form['buildingNumber']
    streetName = request.form['streetName']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    passportNumber = request.form['passportNumber']
    passportExpiration = request.form['passportExpiration']
    country = request.form['country']
    dateOfBirth = request.form['dateOfBirth']


    cursor = conn.cursor()
    query = '''
    INSERT INTO customer(`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    values = (email, name, password, buildingNumber, streetName, city, state, phone, passportNumber, passportExpiration, country, dateOfBirth)

    try:
        # Execute the query
        cursor.execute(query, values)
        conn.commit()
        cursor.close()

        # Redirect or return a success message
        message = "success"
        flash(message)
        return redirect(url_for('register'))
    except Exception as e:
        # Rollback changes if insertion produces an error
        conn.rollback()
        #error = f"Error: {e}"
        message = "error-customer-in-use"
        flash(message)
        return redirect(url_for('register'))

#route to insert new booking agent user into database
@app.route('/registerBookingAgent', methods=['GET', 'POST'])
def registerBookingAgent():
    email = request.form['email']
    password = request.form['password']
    airline = request.form['airline']

    cursor = conn.cursor()
    query = "SELECT MAX(booking_agent_id) FROM booking_agent"

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        agentID = result['MAX(booking_agent_id)'] + 1
        
        query = '''
        INSERT INTO booking_agent(`email`, `password`, `booking_agent_id`)
        VALUES(%s, %s, %s)
        '''

        values = (email, password, agentID)
        cursor.execute(query, values)

        query= '''
        INSERT INTO booking_agent_work_for(`email`, `airline_name`)
        VALUES(%s, %s)
        '''

        values = (email, airline)
        cursor.execute(query, values)

        conn.commit()
        cursor.close()
        message = "success"
        flash(message)
        return redirect(url_for('register'))
    except Exception as e:
        conn.rollback()
        message = f"Error: {e}"
        flash(message)
        return message#redirect(url_for('register'))
    


#route to insert new airline staff user into database
@app.route('/registerAirlineStaff', methods=['GET', 'POST'])
def registerAirlineStaff():
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    dateOfBirth = request.form['dateOfBirth']
    airline = request.form['airline']

    cursor = conn.cursor()
    query = '''
        INSERT INTO airline_staff(`username`,`password`,`first_name`,`last_name`,`date_of_birth`,`airline_name`)
        VALUES (%s, %s, %s, %s, %s, %s);
    '''
    values = (username, password, firstName, lastName, dateOfBirth, airline)

    try:
        cursor.execute(query, values)
        conn.commit()
        cursor.close()

        # Redirect or return a success message
        message = "success"
        flash(message)
        return redirect(url_for('register'))
    except Exception as e:
        conn.rollback()
        error = f"Error: {e}"
        message = "error-staff-in-use"
        flash(message)
        return error#redirect(url_for('register'))

@app.route('/addFlight', methods=['GET', 'POST'])
def addFlight():
    airlineName = request.form['airlineName']
    flightNum = request.form['flightNum']
    departureAirport = request.form['departureAirport']
    departureTime = request.form['departureTime']
    arrivalAirport = request.form['arrivalAirport']
    arrivalTime = request.form['arrivalTime']
    price = request.form['price']
    flightStatus = request.form['flightStatus']
    airplaneID = request.form['airplaneID']

    cursor = conn.cursor()
    query = '''
    INSERT INTO flight(`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    values = (airlineName, flightNum, departureAirport, departureTime, arrivalAirport, arrivalTime, price, flightStatus, airplaneID)
    
    try:
        # Execute the query
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        # Redirect or return a success message
        message = "success"
        flash(message)
        return redirect(url_for('adminDashboard'))
    except Exception as e:
        # Rollback changes if insertion produces an error
        conn.rollback()
        error = f"Error: {e}"
        message = "error-invalid-info"
        flash(message)
        return redirect(url_for('adminDashboard'))

@app.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
    airplaneID = request.form['airplaneID']
    seats = request.form['seats']
    
    cursor = conn.cursor()
    
    query1 = '''
    SELECT airline_name FROM airline_staff
    WHERE airline_staff.username = %s
    '''
    value1 = (session['username'])

    cursor.execute(query1, value1)
    data = cursor.fetchall()
    print(data)

    #probably change to fetchone
    airlineName = data[0]['airline_name']

    query2 = '''
    INSERT INTO airplane(`airline_name`, `airplane_id`, `seats`)
    VALUES (%s, %s, %s)
    '''

    value2 = (airlineName, airplaneID, seats)
    
    try:
        # Execute the query
        cursor.execute(query2, value2)
        conn.commit()
        cursor.close()
        # Redirect or return a success message
        message = "success"
        flash(message)
        return redirect(url_for('adminDashboard'))
    except Exception as e:
        # Rollback changes if insertion produces an error
        conn.rollback()
        error = f"Error: {e}"
        message = "error-invalid-info"
        flash(message)
        return redirect(url_for('adminDashboard'))
    
@app.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
    airportName = request.form['airportName']
    airportCity = request.form['airportCity']
    
    cursor = conn.cursor()
    query = '''
    INSERT INTO airport(`airport_name`, `airport_city` )
    VALUES (%s, %s)
    '''
    values = (airportName, airportCity)
    
    try:
        # Execute the query
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        # Redirect or return a success message
        message = "success"
        flash(message)
        return redirect(url_for('adminDashboard'))
    except Exception as e:
        # Rollback changes if insertion produces an error
        conn.rollback()
        error = f"Error: {e}"
        message = "error-invalid-info"
        flash(message)
        return redirect(url_for('adminDashboard'))

#Define route to display all upcoming flights in the database
@app.route('/displayUpcoming')
def displayUpcoming():
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, departure_airport, arrival_airport, status, departure_time FROM flight WHERE status IN ("On time", "Delayed") ORDER BY departure_time'
    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    error = None
    if (data):
        return render_template('view_flights.html', data=data)
    else:
        error = 'No upcoming flights found'
        return render_template('index.html', error=error)

#define route to display purchased flights
#MUST BE LOGGED IN AS CUSTOMER OR BOOKING AGENT
@app.route('/myFlights')
def myFlights():
    if (is_logged_in() and session['user_type'] == 'customer'):
        cursor = conn.cursor()
        query = '''
        SELECT * FROM flight
        NATURAL JOIN purchases
        NATURAL JOIN ticket
        WHERE purchases.customer_email = %s
        '''
        value = (session['username'])

        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        error=None
        if (data):
            return render_template('view_customer_flights.html', data=data)
        else:
            error = 'No flights found'
            return render_template('view_customer_flights.html', error=error)
    
    else:
        return redirect(url_for('home'))
    
@app.route('/myAccount')
def myAccount():
    if (is_logged_in()):
        return render_template('account_display.html')
    else:
        return redirect(url_for('login'))

@app.route('/purchase/<int:flightNum>', methods=['GET', 'POST'])
def purchase(flightNum):
    if (is_logged_in()):
        cursor = conn.cursor()
        query = '''
        SELECT airline_name
        FROM flight  
        WHERE flight_num = %s
        '''
        cursor.execute(query, flightNum)
        
        data = cursor.fetchone()
        airlineName = data['airline_name']

        query = "SELECT MAX(ticket_id) FROM ticket"
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            ticketID = result['MAX(ticket_id)'] + 1
            
            query = '''
            INSERT INTO ticket(`ticket_id`, `airline_name`, `flight_num`)
            VALUES(%s, %s, %s)
            '''

            values = (ticketID, airlineName, flightNum)
            cursor.execute(query, values)

            query_cust= '''
            INSERT INTO purchases(`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`)
            VALUES(%s, %s, NULL, %s)
            '''

            query_agent = '''
            INSERT INTO purchases(`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`)
            VALUES(%s, %s, %s, %s)
            '''

            today = date.today()

            email = ""
            if(session['user_type'] == 'booking_agent'):
                email = request.form['customerEmail']
                id_query = '''
                SELECT booking_agent_id
                FROM booking_agent
                WHERE email = %s
                '''
                values = (session['username'])
                cursor.execute(id_query, values)
                result = cursor.fetchone()
                agentID = result['booking_agent_id']
                values = (ticketID, email, agentID, today)

                cursor.execute(query_agent, values)

            else:
                email = (session['username'])
                values = (ticketID, email, today)

                cursor.execute(query_cust, values)

            conn.commit()
            cursor.close()
            # Redirect or return a success message
            message = "purchase-success"
            flash(message)
            cursor.close()
            return redirect(url_for('home'))
        except Exception as e:
            conn.rollback()
            error = f"Error: {e}"
            message = "purchase-error"
            flash(message)
            return error
    else:
        message = "error-not-registered"
        flash(message)
        return redirect(url_for('register'))
    
#TODO route to render admin dashboard for authenticated staff with admin permissions
@app.route('/admin/dashboard')
def adminDashboard():
    if (is_logged_in() and session['permission'] == 'admin'):
        cursor = conn.cursor()
        query = '''
        SELECT * FROM airplane
        NATURAL JOIN airline_staff
        WHERE airline_staff.username = %s
        '''
        value = (session['username'])

        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        error=None
        if (data):
            return render_template('admin.html', data=data)
        else:
            error = 'No airplanes found'
            return render_template('admin.html', error=error) 
    else:
        return make_response(render_template('403.html'), 403)

#TODO implement route to display top destinations
@app.route('/displayDestinations')
def displayDestinations():
    cursor = conn.cursor()
    queryCities = '''
        SELECT airport_city, COUNT(*) AS ticket_count
        FROM (
            SELECT airport.airport_city
            FROM ticket
            INNER JOIN flight ON ticket.flight_num = flight.flight_num
            INNER JOIN airport ON flight.arrival_airport = airport.airport_name
        ) AS subquery
        GROUP BY airport_city
        ORDER BY ticket_count DESC
        LIMIT 3;
    '''
    cursor.execute(queryCities)
    data = cursor.fetchall()
    return render_template('destinations_display.html', data=data)


### error handling ###
@app.errorhandler(404)  
def not_found(e):
    return render_template('404.html')

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html')

@app.errorhandler(401)
def invalid_credentials(e):
    return render_template('401.html')

@app.errorhandler(400)  
def bad_request(e):
    return render_template('400.html')




#temporary routes for development REMOVE 
@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/test')
def test():
    return render_template('test.html')




#initialization
app.secret_key = 'H2O intolerant'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)