from flask import Flask, render_template, session, request, url_for, redirect
import pymysql.cursors

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

@app.route('/searchFlights', methods=['GET', 'POST'])
def searchFlights():
    departureCity = request.form['departureCity']
    arrivalCity = request.form['arrivalCity']
    departureAirport = request.form['departureAirport']
    arrivalAirport = request.form['arrivalAirport']
    #year = request.form['year']
    #month = request.form['month']
    #day = request.form['day']

    conditions = []
    params = []

    if departureCity:
        conditions.append("a.city = %s")
        params.append(departureCity)
    if arrivalCity:
        conditions.append("b.city = %s")
        params.append(arrivalCity)
    if departureAirport:
        conditions.append("flight.dep_airport = %s")
        params.append(departureAirport)
    if arrivalAirport:
        conditions.append("flight.arr_airport = %s")
        params.append(arrivalAirport)

    error = None

    if not any([departureCity, arrivalCity, departureAirport, arrivalAirport]):
        error = "Please fill at least one field"
        return render_template('home.html', error=error)

    cursor = conn.cursor()

    query = '''
        SELECT flight.*, a.city AS departure_city, b.city AS arrival_city
        FROM flight 
        INNER JOIN airport AS a ON flight.dep_airport = a.name 
        INNER JOIN airport AS b ON flight.arr_airport = b.name 
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

@app.route('/login')
def login():
    return render_template('login.html')

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
        SELECT 'customer' AS user_type, email, password FROM customer WHERE email = %s AND password = %s
        UNION
        SELECT 'airline_staff' AS user_type, username AS email, password FROM airline_staff WHERE username = %s AND password = %s
        UNION
        SELECT 'booking_agent' AS user_type, email, password FROM booking_agent WHERE email = %s AND password = %s
    '''
    cursor.execute(query, (username, password, username, password, username, password))

    data = cursor.fetchone()

    cursor.close()
    error = None
    if (data):
        session['username'] = username
        session['permission'] = data['user_type']
        return redirect(url_for('home'))
    else:
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

@app.route('/register')
def register():
    return render_template('register.html')

#Define route to display all upcoming flights in the database
@app.route('/displayUpcoming')
def displayUpcoming():
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, dep_airport, arr_airport, status FROM flight WHERE status IN ("upcoming", "delayed")'
    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    error = None
    if (data):
        return render_template('display_upcoming.html', data=data)
    else:
        error = 'No upcoming flights found'
        return render_template('index.html', error=error)

#define route to display purchased flights
#MUST BE LOGGED IN WITH CUSTOMER PERMISSION
@app.route('/myFlights')
def my_flights():
    return render_template('view_my_flights.html')




### error handling ###
@app.errorhandler(404)  
def not_found(e):
    return render_template('404.html')

@app.errorhandler(400)  
def not_found(e):
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