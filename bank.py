import hashlib
from flask import *
import mysql.connector 
from datetime import datetime


app= Flask(__name__)
app.secret_key = "your_secret_key"


# Database config #---------------------------------------------------------------------------------------------------------
db_config = {
    'host': 'localhost', #bank.crqmssgockvo.ap-south-1.rds.amazonaws.com
    'user': 'root',
    'password': '',
    'database': 'AWS_Bank'
}

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",pool_size=5,**db_config)

def get_db_connection():
    try:
        return cnxpool.get_connection()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

#-------------------------------------------------------------------------------------------------------------------------------------

#--REGISTER------------------------------------------------------------------------------------------------------------------------------


@app.route('/register')
def renderRegister():
    return render_template("register.html")



# @app.route('/loginValidate',methods=['POST'])
# def validateLogin():
#     email=request.form['email']
#     password=request.form['password']

#     if not email or not password:
#         flash("Please Enter email and password both",'error')
#         return redirect("/login")
    
#     user = check_credentials(email, password)
    
#     if user:
#         flash("Login Successful",'success')
#         return redirect("/dashboard")
#     else:
#         flash("Invalid credentials, please try again", 'error')
#         return redirect("/")


@app.route('/registeringUser',methods=['POST'])
def getDataFromForm():   
    fn = request.form['firstname']
    ln = request.form['lastname']
    email = request.form['email']
    aadhar = request.form['aadhar']
    password = request.form['password']
    address = request.form['address']

    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute("Insert into users   ")


    return ":"


#----------------------------------------------------------------------------------------------------------------------------------------

# NEXT SECTION

#--LOGIN------------------------------------------------------------------------------------------------------------------------------


@app.route('/login')

def renderLogin():
    return render_template("login.html")

def check_credentials(email, password):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # hashed_password = hashlib.sha256(password.encode()).hexdigest()
    hashed_password = password 
    
    cursor.execute("SELECT * FROM users WHERE email = %s AND pass = %s", (email, hashed_password))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return user

@app.route('/loginValidate',methods=['POST'])
def validateLogin():
    email=request.form['email']
    password=request.form['password']

    if not email or not password:
        flash("Please Enter email and password both",'error')
        return redirect("/login")
    
    user = check_credentials(email, password)
    
    if user:
        flash("Login Successful",'success')
        return redirect("/dashboard")
    else:
        flash("Invalid credentials, please try again", 'error')
        return redirect("/")

#-------------------------------------------------------------------------------------------------------------------------------------------------
    



#--------------------CONTACT---------------------------------------------------

@app.route('/contact')
def renderContact():
    return render_template("contact.html")

#------------------Service---------------------------------------------------

@app.route('/services')
def renderService():
    return render_template("services.html")



#-----------------Main-----------------
@app.route('/')
def renderHome():
    return render_template("index2.html")





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
    return render_template('dashboard_old.html')
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