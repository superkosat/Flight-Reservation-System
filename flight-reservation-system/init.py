from flask import Flask, render_template, session, request, url_for, redirect
import pymysql.cursors

app = Flask(__name__)

#Establish connection to MySQL server
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='airline_test_3',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define routes

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('display_upcoming'))
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear
    return redirect(url_for('login'))

#route for login authentication
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
    cursor.execute(query, (username, password))

    data = cursor.fetchone()

    cursor.close()
    error = None
    if (data):
        session['username'] = username
        return redirect(url_for('display_upcoming'))
    else:
        error = 'Invalid username or password'
        return render_template('login.html', error=error)

@app.route('/register')
def register():
    return render_template('register.html')

#Define route to display all upcoming flights in the database
@app.route('/display_upcoming')
def display_upcoming():
    cursor = conn.cursor()
    query = 'SELECT airline_name, flight_num, dep_airport, arr_airport FROM flight WHERE status = "upcoming"'
    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    error = None
    if (data):
        return render_template('display_upcoming.html', data=data)
    else:
        error = 'No upcoming flights found'
        return render_template('index.html', error=error)
    
@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/test')
def test():
    return render_template('test.html')

app.secret_key = 'H2O intolerant'


if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)