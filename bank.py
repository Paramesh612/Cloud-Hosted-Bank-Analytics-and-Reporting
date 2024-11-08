#from flask import Flask, render_template, request, session
from flask import *
import mysql.connector
from datetime import datetime





app= Flask(__name__)
app.secret_key = "your_secret_key"


# Database config
db_config = {
    'host': 'localhost', #bank.crqmssgockvo.ap-south-1.rds.amazonaws.com
    'user': '',
    'password': '',
    'database': 'bank'
}

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",pool_size=5,**db_config)


@app.route('/')
def renderHome():
    return render_template("index2.html")

@app.route('/register')
def renderRegister():
    return render_template("register.html")

@app.route('/login')
def renderLogin():
    return render_template("login.html")


def get_db_connection():
    try:
        return cnxpool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route("/test-db-connection")
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE() ;")
        db_name = cursor. fetchone()
        cursor.close()
        conn. close()
        return f"Connected to the database: {db_name[0]}"
    except mysql.connector.Error as err:
        return f"Error: {err}"

    






@app.route("/dashboard")
def dashboard():

    user_data = session.get('user')

    if user_data:

        email = user_data['email']

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

        user = cursor.fetchone()

        cursor.close()

        conn.close()

        return render_template("dashboard.html", user=user)
    else:
          return redirect("/login")



   

@app.route("/deposit", methods=['post', 'get'])

def deposit():

    user_data = session.get('user')

    if user_data:

        if request.method == 'POST':

            amount = float(request.form['deposit_amount'])

            account_type = request.form['account_type']

            conn = get_db_connection()

            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM accounts WHERE user_id = %s", (user_data['user_id'],))

            if not cursor.fetchone():

                # Insert a new row

                cursor.execute("INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)", (user_data['user_id'], amount, account_type))

                cursor.execute("INSERT INTO account_statements (user_id, transaction_type,transaction_amount, transaction_date) VALUES (%s, 'Credit', %s, %s)", (user_data['user_id'], amount, datetime.now()))

            else:

                # Update the existing row

                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s", (amount, user_data['user_id']))

                cursor.execute("INSERT INTO account_statements (user_id, transaction_type,transaction_amount,  transaction_date) VALUES (%s, 'Credit', %s, %s)", (user_data['user_id'], amount, datetime.now()))

            conn.commit()

            cursor.close()

            conn.close()

            flash("Funds deposited successfully!")

            return redirect(url_for('dashboard'))

        return render_template("deposit.html")

    else:

        return redirect(url_for('login'))
    

if __name__=='__main__':
    app.run(debug=True) 