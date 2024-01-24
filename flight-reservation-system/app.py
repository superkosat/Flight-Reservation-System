from flask import Flask, render_template, session, request, url_for, redirect, flash, abort, make_response
from werkzeug.security import generate_password_hash, check_password_hash
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
        SELECT 'customer' AS user_type, email, password, name FROM customer WHERE email = %s
        UNION
        SELECT 'airline_staff' AS user_type, username AS email, password, first_name FROM airline_staff WHERE username = %s
        UNION
        SELECT 'booking_agent' AS user_type, email, password, booking_agent_id FROM booking_agent WHERE email = %s
    '''
    cursor.execute(query, (username, username, username))

    data = cursor.fetchone()
    print(data)
    error = None
    if data:
        stored_password = data['password']
        if check_password_hash(stored_password, password):
            session['username'] = username
            session['user_type'] = data['user_type']
            session['name'] = data['name']
            if session['user_type'] == 'airline_staff':
                query = "SELECT permission_type FROM permission NATURAL JOIN airline_staff WHERE username = %s"
                cursor.execute(query, (username))
                data = cursor.fetchone()
                if data==None:
                    session['permission'] = None
                else:
                    session['permission'] = data['permission_type']

            # Add additional data to the session if needed

            cursor.close()
            return redirect(url_for('home'))
        else:
            error = 'Invalid password'
            print(stored_password)
            print(password)
            print(check_password_hash(generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), password))
    else:
        error = 'Invalid username or password'

    cursor.close()
    return render_template('login.html', error=error)


    #error = None
    #if (data):
    #    session['username'] = username
    #    session['user_type'] = data['user_type']
    #    session['name'] = data['name']
    #    if session['user_type'] == 'airline_staff':
    #        query = "SELECT permission_type FROM permission NATURAL JOIN airline_staff WHERE username = %s"
    #        cursor.execute(query, (username))
    #        data = cursor.fetchone()
    #        session['permission'] = data['permission_type']
    #    cursor.close()
    #    return redirect(url_for('home'))
    #else:
    #    cursor.close()
    #    error = 'Invalid username or password'
    #    return render_template('login.html', error=error)

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
    password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)
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
    password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)

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
    password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)
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
#MUST BE LOGGED IN AS CUSTOMER
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
        if(session['user_type'] == 'customer'):
            return redirect(url_for('customerAccount'))
        elif(session['user_type'] == 'booking_agent'):
            return redirect(url_for('agentAccount'))
        elif(session['user_type'] == 'airline_staff'):
            return redirect(url_for('staffAccount'))
    else:
        return redirect(url_for('login'))
    
@app.route('/filterComms',  methods=['GET', 'POST'])
def filterComms():
    startDate = request.form['startDate']
    endDate = request.form['endDate']
    params = [startDate, endDate]
    return agentAccount(params)

@app.route('/agent/account')
def agentAccount(params = ['a','b']):
    if (is_logged_in() and session['user_type'] == 'booking_agent'):
        startDate = params[0]
        endDate = params[1]
        start = ""
        end = ""
        active_tab = 'list-profile'
        if(startDate != 'a'):
            active_tab = 'list-sales-report'
        value = session['username']
        values = [value]
        cursor = conn.cursor()

        #get agent info
        query = '''SELECT * FROM booking_agent
                    LEFT JOIN booking_agent_work_for
                    ON booking_agent.email = booking_agent_work_for.email
                    WHERE booking_agent.email = %s'''
        cursor.execute(query, value)
        data = cursor.fetchone()

        #get flights
        query = '''SELECT * FROM flight
        NATURAL JOIN purchases
        NATURAL JOIN ticket
        NATURAL JOIN booking_agent
        WHERE booking_agent.email = %s
        '''
        
        cursor.execute(query, value)
        flights = cursor.fetchall()

        #add date filtering with if statement
        #get agent's commissions
        query1 = '''
        SELECT SUM(f.price * 0.1) AS commissions,
        COUNT(*) as total_sales
        FROM 
            booking_agent AS ba
        JOIN 
            purchases AS p ON ba.booking_agent_id = p.booking_agent_id
        JOIN 
            ticket AS t ON p.ticket_id = t.ticket_id
        JOIN 
            flight AS f ON t.flight_num = f.flight_num
        WHERE 
            ba.email = %s
        AND
        	p.purchase_date BETWEEN CONVERT( %s , DATETIME) AND CONVERT( %s , DATETIME);
        '''
        query2 = '''
        SELECT SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN f.price * 0.1 ELSE 0 END) AS commissions,
        COUNT(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN 1 ELSE 0 END) AS total_sales
        FROM 
            booking_agent AS ba
        JOIN 
            purchases AS p ON ba.booking_agent_id = p.booking_agent_id
        JOIN 
            ticket AS t ON p.ticket_id = t.ticket_id
        JOIN 
            flight AS f ON t.flight_num = f.flight_num
        WHERE 
            ba.email = %s
        '''
        
        if(startDate != 'a'):
            start = startDate
            end = endDate
            values.append(start)
            values.append(end)
            cursor.execute(query1, values)
        else:
            cursor.execute(query2, values)
        commissions = cursor.fetchall()
        if(commissions[0]['commissions'] != None):
            commissions[0]['commissions'] = int(commissions[0]['commissions'])
        elif(commissions[0]['commissions'] == None and params[0] != 'a'):
            commissions[0]['commissions'] = 0
        #total_sales unnecessary here I think

        #get top 5 customers by number sales last 6 months: need to make it just 5
        query = '''
        SELECT c.*, COUNT(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 6 MONTH AND CURDATE() THEN 1 ELSE 0 END) AS tickets_purchased
        FROM customer c
        JOIN purchases p ON c.email = p.customer_email
        JOIN booking_agent AS ba on ba.booking_agent_id = p.booking_agent_id
        WHERE ba.email = %s
        GROUP BY c.email
        '''
        cursor.execute(query, value)
        customerSales = cursor.fetchall()

        emails = []
        sales = []
        for customer in customerSales:
            customer["tickets_puchased"] = str(customer["tickets_purchased"])
            emails.append(customer["email"])
            sales.append(customer["tickets_purchased"])
        emailsLimit = []
        salesLimit = []
        i = 0
        if(len(emails) != 0):
            while(len(emailsLimit) < 5):
                emailsLimit.append(emails[i])
                salesLimit.append(sales[i])
                i += 1
                if(len(emailsLimit) == len(emails)):
                    break
        emails = emailsLimit
        sales = salesLimit

        
        saleData = {
            'emails': emails,
            'sales': sales
        }
        
        #get top 5 customers by total commission: need to make it just 5
        query = '''
        SELECT c.*, 
        SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 365 DAY AND CURDATE() THEN f.price * 0.1 ELSE 0 END) AS past_year_commissions
        FROM customer c
        JOIN purchases p ON c.email = p.customer_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight AS f ON t.flight_num = f.flight_num
        JOIN booking_agent AS ba on ba.booking_agent_id = p.booking_agent_id
        WHERE ba.email = %s
        GROUP BY c.email
        '''

        cursor.execute(query, value)
        customerComms = cursor.fetchall()

        emails = []
        comms = []
        for customer in customerComms:
            customer["past_year_commissions"] = str(int(customer["past_year_commissions"]))
            emails.append(customer["email"])
            comms.append(customer["past_year_commissions"])
        emailsLimit = []
        commsLimit = []
        i = 0
        if(len(emails) != 0):
            while(len(emailsLimit) < 5):
                emailsLimit.append(emails[i])
                commsLimit.append(comms[i])
                i += 1
                if(len(emailsLimit) == len(emails)):
                    break
        emails = emailsLimit
        comms = commsLimit
        
        commsData = {
            'emails': emails,
            'comms': comms,
        }

        cursor.close()
        return render_template('agent_account_display.html', saleData=saleData, commsData = commsData, commissions = commissions, flights=flights, data=data, active_tab=active_tab)
    else:
        return make_response(render_template('403.html'), 403)

@app.route('/filterSales',  methods=['GET', 'POST'])
def filterSales():
    startDate = request.form['startDate']
    endDate = request.form['endDate']
    params = [startDate, endDate]
    return staffAccount(params)

@app.route('/staff/account')
def staffAccount(params = ['a','b']):
    if (is_logged_in() and session['user_type'] == 'airline_staff'):
        startDate = params[0]
        endDate = params[1]
        start = ""
        end = ""
        active_tab = 'list-profile'
        if(startDate != 'a'):
            active_tab = 'list-sales-report'
        value = session['username']
        cursor = conn.cursor()

        #get staff info
        query = "SELECT * FROM airline_staff WHERE username = %s"
        cursor.execute(query, value)
        data = cursor.fetchone()

        #get flights
        query = "SELECT * FROM flight WHERE airline_name = (SELECT airline_name FROM airline_staff WHERE username = %s)"
        cursor.execute(query, value)
        flights = cursor.fetchall()

        #get agents

        query='''
        SELECT 
        ba.booking_agent_id,
        ba.email,
        SUM(f.price * 0.1) AS past_year_commissions,
        SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN f.price * 0.1 ELSE 0 END) AS past_month_commissions,
        COUNT(*) AS total_sales,
        SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 365 DAY AND CURDATE() THEN 1 ELSE 0 END) AS sales_past_year,
        SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN 1 ELSE 0 END) AS sales_past_month
        FROM 
            booking_agent AS ba
        JOIN 
            purchases AS p ON ba.booking_agent_id = p.booking_agent_id
        JOIN 
            ticket AS t ON p.ticket_id = t.ticket_id
        JOIN 
            flight AS f ON t.flight_num = f.flight_num
        JOIN 
            booking_agent_work_for AS bawf ON ba.email = bawf.email
        JOIN 
            airline_staff AS als ON bawf.airline_name = als.airline_name
        WHERE 
            als.username = %s
        GROUP BY 
            ba.booking_agent_id, ba.email
        ORDER BY 
            past_year_commissions DESC
        '''
        cursor.execute(query, value)
        agents = cursor.fetchall()

        #get direct sales
        query='''
        SELECT SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN f.price ELSE 0 END) AS past_month_total,
            SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 365 DAY AND CURDATE() THEN f.price ELSE 0 END) AS past_year_total
        FROM 
            purchases AS p 
        JOIN 
            ticket AS t ON p.ticket_id = t.ticket_id
        JOIN 
            flight AS f ON t.flight_num = f.flight_num
        WHERE 
            p.booking_agent_id IS NULL
        AND t.airline_name = %s
        '''
        cursor.execute(query, data['airline_name'])
        direct = cursor.fetchall()

        #get indirect sales
        query='''
        SELECT SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() THEN f.price ELSE 0 END) AS past_month_total,
            SUM(CASE WHEN p.purchase_date BETWEEN CURDATE() - INTERVAL 365 DAY AND CURDATE() THEN f.price ELSE 0 END) AS past_year_total
        FROM 
            purchases AS p 
        JOIN 
            ticket AS t ON p.ticket_id = t.ticket_id
        JOIN 
            flight AS f ON t.flight_num = f.flight_num
        WHERE 
            p.booking_agent_id IS NOT NULL
        AND t.airline_name = %s
        '''
        cursor.execute(query, data['airline_name'])
        indirect = cursor.fetchall()

        mDirPer = 0
        mIndPer = 0
        if(direct[0]['past_month_total'] == None):
            direct[0]['past_month_total'] = 0
            mDirPer = 0
            mIndPer = 100
        elif(indirect[0]['past_month_total'] == None):
            indirect[0]['past_month_total'] = 0
            mDirPer = 100
            mIndPer = 0
        else:
            mDirPer = int(100*((direct[0]['past_month_total']) / (direct[0]['past_month_total'] + indirect[0]['past_month_total'])))
            mIndPer = 100 - mDirPer

        yDirPer = 0
        yIndPer = 0
        if(direct[0]['past_year_total'] == None):
            direct[0]['past_year_total'] = 0
            yDirPer = 0
            yIndPer = 100
        elif(indirect[0]['past_year_total'] == None):
            indirect[0]['past_year_total'] = 0
            yDirPer = 100
            yIndPer = 0
        else:
            yDirPer = int(100*((direct[0]['past_year_total']) / (direct[0]['past_year_total'] + indirect[0]['past_year_total'])))
            yIndPer = 100 - yDirPer
        
        salesComp = {
            'directMonthly': str(direct[0]['past_month_total']),
            'directYearly': str(direct[0]['past_year_total']),
            'indirectMonthly': str(indirect[0]['past_month_total']),
            'indirectYearly': str(indirect[0]['past_year_total']),
            'mDirPercent':str(mDirPer),
            'mIndPercent':str(mIndPer),
            'yDirPercent':str(yDirPer),
            'yIndPercent':str(yIndPer)
        }

        #get top customers
        query = '''
        SELECT c.*, COUNT(p.ticket_id) AS tickets_purchased
        FROM customer c
        JOIN purchases p ON c.email = p.customer_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN airline_staff a ON t.airline_name = a.airline_name
        WHERE a.username = %s
        GROUP BY c.email
        '''
        cursor.execute(query, value)
        customers = cursor.fetchall()

        #get customer flights
        query = '''
        SELECT * FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN customer c ON p.customer_email = c.email
        WHERE f.airline_name = (SELECT airline_name FROM airline_staff WHERE username = %s)
        '''
        cursor.execute(query, value)
        customerFlights = cursor.fetchall()

        #get sales report data
        
        conditions = ["ticket.airline_name = %s"]

        values = [data['airline_name']]

        if(startDate != 'a'):
            conditions.append(" purchases.purchase_date BETWEEN %s and %s")
            values.append(startDate)
            values.append(endDate)
        query = '''
        SELECT purchase_date FROM flight
        NATURAL JOIN purchases
        NATURAL JOIN ticket
        WHERE {}
        '''.format(" AND ".join(conditions))
    
        cursor = conn.cursor()
        cursor.execute(query, values)
        totalSales = cursor.fetchall()
        monthlySales = []
        months = []
        monthDict = {
            '1': "Jan",
            '2': "Feb",
            '3': "Mar",
            '4': "Apr",
            '5': "May",
            '6': "Jun",
            '7': "Jul",
            '8': "Aug",
            '9': "Sept",
            '10': "Oct",
            '11': "Nov",
            '12': "Dec"
        }

        sumAssign = {
            "01": 0,
            "02": 1,
            "03": 2,
            "04": 3,
            "05": 4,
            "06": 5,
            "07": 6,
            "08": 7,
            "09": 8,
            "10": 9,
            "11": 10,
            "12": 11
        }

        if(startDate != 'a'):
            start = int((str(startDate))[5:7])
            end = int((str(endDate))[5:7])
            for i in range(start, end + 1):
                months.append(monthDict[str(i)])
                monthlySales.append(0)
            for purchase in totalSales:
                pdate = purchase['purchase_date']
                sdate = int(str(pdate)[5:7]) - start
                monthlySales[sdate] += 1
        else:
            monthlySales = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]
            for purchase in totalSales:
                pdate = purchase['purchase_date']
                pdate = str(pdate)[5:7]
                monthlySales[sumAssign[pdate]] += 1
        total = 0
        for i in range(0, len(monthlySales)):
            total += monthlySales[i]
            monthlySales[i] = str(monthlySales[i])
        total = str(total)

        saleReport = {
            'months': months,
            'sales': monthlySales,
            'total': total
        }
        cursor.close()
        return render_template('staff_account_display.html', customerFlights=customerFlights, salesComp = salesComp, customers=customers, agents=agents, flights=flights, saleReport=saleReport, data=data, active_tab=active_tab)
    else:
        return make_response(render_template('403.html'), 403)
    
@app.route('/staff/view/flights')
def staffViewFlights():
    if (is_logged_in() and session['user_type'] == 'airline_staff'):
        active_tab = 'list-flights'
        return redirect(url_for('staffAccount'))
    else:
        return make_response(render_template('403.html'), 403)


#TODO route to render operator dashboard for authenticated staff with operator permissions
@app.route('/operator/dashboard')
def operatorDashboard():
    if (is_logged_in() and session['permission'] == 'operator'):
        return render_template('operator.html')
    else:
        return make_response(render_template('403.html'), 403)
    
@app.route('/operator/changeFlightStatus', methods=['POST'])
def changeFlightStatus():
    if (is_logged_in() and session['permission'] == 'operator'):
        flightNum = request.form['flightNum']
        flightStatus = request.form['flightStatus']

        cursor = conn.cursor()

        query = "SELECT * FROM flight WHERE flight_num = %s"
        cursor.execute(query, flightNum)
        data = cursor.fetchone()
        if not data:
            message = "error-invalid-flight"
            flash(message)
            return redirect(url_for('operatorDashboard'))
        
        try:
            query = '''
            UPDATE flight
            SET status = %s
            WHERE flight_num = %s;
            '''
            cursor.execute(query, (flightStatus, flightNum))
            conn.commit()
            cursor.close()
            message = "success"
            flash(message)
            return redirect(url_for('operatorDashboard'))
        except Exception as e:
            conn.rollback()
            error = f"Error: {e}"
            message = "error-invalid-flight"
            flash(message)
            return redirect(url_for('operatorDashboard'))
    else:
        return make_response(render_template('403.html'), 403)

#couple of minor changes necessary:
#after filtering dates default to spending tab
#should show past 6 months by default not whole year: use date.today
#also there's no way to set a purchase date manually outside to be able to see purchases across months
#(just sets to current date right now)
@app.route('/filterDate',  methods=['GET', 'POST'])
def filterDate():
    startDate = request.form['startDate']
    endDate = request.form['endDate']
    params = [startDate, endDate]
    return customerAccount(params)
    
@app.route('/customerAccount')
def customerAccount(params = ['a','b']):
    if (is_logged_in() and session['user_type'] == 'customer'):
        startDate = params[0]
        endDate = params[1]
        conditions = ["purchases.customer_email = %s"]

        value = [session['username']]

        if(startDate != 'a'):
            conditions.append(" purchases.purchase_date BETWEEN %s and %s")
            value.append(startDate)
            value.append(endDate)
        query = '''
        SELECT price, purchase_date FROM flight
        NATURAL JOIN purchases
        NATURAL JOIN ticket
        WHERE {}
        '''.format(" AND ".join(conditions))
    
        cursor = conn.cursor()
        cursor.execute(query, value)
        data = cursor.fetchall()
      
        #get customer info
        query = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query, value[0])
        custData = cursor.fetchone()

        cursor.close()

        monthly_sums = []
        months = []
        monthDict = {
            '1': "Jan",
            '2': "Feb",
            '3': "Mar",
            '4': "Apr",
            '5': "May",
            '6': "Jun",
            '7': "Jul",
            '8': "Aug",
            '9': "Sept",
            '10': "Oct",
            '11': "Nov",
            '12': "Dec"
        }

        if(startDate != 'a'):
            start = int((str(startDate))[5:7])
            end = int((str(endDate))[5:7])
            for i in range(start, end + 1):
                months.append(monthDict[str(i)])
                monthly_sums.append(0)
            for purchase in data:
                pdate = purchase['purchase_date']
                sdate = int(str(pdate)[5:7]) - start
                monthly_sums[sdate] += purchase['price']
        else:
            dStart = date.today()
            end = int((str(dStart))[5:7])
            start = end - 5
            for i in range(start, end + 1):
                months.append(monthDict[str(i)])
                monthly_sums.append(0)
            for purchase in data:
                pdate = purchase['purchase_date']
                sdate = int(str(pdate)[5:7]) - start
                if(sdate >= 0):
                    monthly_sums[sdate] += purchase['price']

        total = 0
        for i in range(0, len(monthly_sums)):
            total += monthly_sums[i]
            monthly_sums[i] = str(monthly_sums[i])
        total = str(total)

        data = {
            'months': months,
            'sums': monthly_sums,
            'total': total
        }

        return render_template('account_display.html', data=data, custData = custData)
    else:
        return redirect(url_for('login'))

@app.route('/purchase/<int:flightNum>', methods=['GET', 'POST'])
def purchase(flightNum):
    if (is_logged_in()):

        cursor = conn.cursor()

        queryFlightRemainingSeats = '''
            SELECT (
                (SELECT seats FROM flight INNER JOIN airplane ON flight.airplane_id = airplane.airplane_id WHERE flight.flight_num = %s) 
                    - 
                (SELECT COUNT(ticket_id) FROM ticket WHERE flight_num = %s)
            ) AS remaining_seats
        '''

        cursor.execute(queryFlightRemainingSeats, (flightNum, flightNum))
        remainingSeats = cursor.fetchone()['remaining_seats']

        if (remainingSeats <= 0):
            message = "error-no-seats"
            flash(message)
            return redirect(url_for('home'))


        query = '''
        SELECT airline_name
        FROM flight  
        WHERE flight_num = %s
        '''
        cursor.execute(query, flightNum)
        
        data = cursor.fetchone()
        airlineName = data['airline_name']

        if (session['user_type'] == 'airline_staff'):
            return redirect(url_for('staffAccount'))
        
        if (session['user_type'] == 'booking_agent'):
            query = "SELECT airline_name FROM booking_agent_work_for WHERE email = %s"
            cursor.execute(query, session['username'])
            agentAirlineNames = cursor.fetchall()
            print(agentAirlineNames)
            print(airlineName)
            agent_airlines = [agent['airline_name'] for agent in agentAirlineNames]
            if airlineName not in agent_airlines:
                message = "agent-error"
                flash(message)
                return redirect(url_for('home'))
        

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
    
#route to render admin dashboard for authenticated staff with admin permissions
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
    
@app.route('/admin/modifyPermission', methods = ['POST'])
def modifyPermission():
    if (is_logged_in() and session['permission'] == 'admin'):
        username = request.form['username']
        permission = request.form['permission']

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM permission WHERE username = %s", (username))
            existing_record = cursor.fetchone()

            if existing_record:
                # If the record exists, update the permission_type
                cursor.execute("UPDATE permission SET permission_type = %s WHERE username = %s", (permission, username))
                conn.commit()
            else:
                # If the record doesn't exist, create a new entry
                cursor.execute("INSERT INTO permission (`username`, `permission_type`) VALUES (%s, %s)", (username, permission))
                conn.commit()

            cursor.close()
            message = "success"
            flash(message)
            return redirect(url_for('adminDashboard'))
        except Exception as e:
            conn.rollback()
            # for debugging - error = f"Error: {e}"
            message = "error-invalid-info"
            flash(message)
            return redirect(url_for('adminDashboard'))
    else:
        return make_response(render_template('403.html'), 403)
    
@app.route('/admin/addBookingAgent', methods=['POST'])
def addBookingAgent():
    if (is_logged_in() and session['permission'] == 'admin'):
        bookingAgentEmail = request.form['email']
        
        cursor = conn.cursor()
        query = '''
            INSERT INTO booking_agent_work_for(`email`, `airline_name`)
            VALUES (%s, %s);
        '''

        try:
            cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (session['username']))
            bookingAgentAirline = cursor.fetchone()['airline_name']
            values = (bookingAgentEmail, bookingAgentAirline)
            cursor.execute(query, values)
            conn.commit()
            message = "success"
            flash(message)
            return redirect(url_for('adminDashboard'))
        except Exception as e:
            conn.rollback()
            #for debugging - error = f"Error: {e}"
            message = "error-invalid-info"
            flash(message)
            return redirect(url_for('adminDashboard'))
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