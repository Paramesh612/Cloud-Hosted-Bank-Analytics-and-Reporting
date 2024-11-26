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


@app.route('/registerUser',methods=['POST','GET'])
def getDataFromForm():   
    fn = request.form['fullname']
    
    email = request.form['email']
    aadhar = request.form['aadhar']
    password = request.form['password']
    phone = request.form['phone_number']
    address = request.form['address']
    pan = request.form['pan']

    print("is db working ?")
    conn = get_db_connection()
    print("yes con is made ")
    
    cursor = conn.cursor()
    stmt = "INSERT INTO users (full_name, email,pass,phone,address,aadhar,pan) VALUES (%s, %s, %s, %s, %s, %s,%s)"
    values = (fn, email,password,phone,address, aadhar,pan)
    try:
        print("hiiiiii")
        cursor.execute(stmt, values)
        print("helllooo")
        conn.commit()  
        return redirect('/login')  
    except Exception as e:
        print(f"Error: {e}")
        return redirect('/register')  
    finally:
        cursor.close()
        conn.close()


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

        #creating session 
        session["user"] = user 

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("select balance from accounts where user_id = %s",(user['user_id'],))
        bal = cursor.fetchone() 
        if bal:
         session["user"] = {**user, 'balance': bal['balance']}


        return redirect("/dashboard")
    else:
        flash("Invalid credentials, please try again", 'error')
        return redirect("/")
    


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


#-------------------------------------------------------------------------------------------------------------------------------------------------
    



#--------------------CONTACT---------------------------------------------------

@app.route('/contact')
def renderContact():
    return render_template("contact.html")

#------------------Service---------------------------------------------------

@app.route('/services')
def renderService():
    return render_template("services.html")

@app.route('/support')
def renderSupport():
    return render_template("support.html")


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

    print(session)  # Check the contents of the session
    user_data = session.get('user')
    print(user_data)

    if user_data:

        if request.method == 'POST':

            amount = float(request.form['deposit_amount'])

            account_type = request.form['account_type']

            descrip = request.form['desc']

            conn = get_db_connection()

            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM accounts WHERE user_id = %s", (user_data['user_id'],))

            if not cursor.fetchone():

                # Insert a new row

                cursor.execute("INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)", (user_data['user_id'], amount, account_type))

                cursor.execute("INSERT INTO account_statements (user_id, transaction_type,transaction_amount, transaction_date,description) VALUES (%s, 'Credit', %s, %s,%s)", (user_data['user_id'], amount, datetime.now(),descrip))

            else:

                # Update the existing row

                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s", (amount, user_data['user_id']))

                cursor.execute("INSERT INTO account_statements (user_id, transaction_type,transaction_amount,  transaction_date,description) VALUES (%s, 'Credit', %s, %s,%s)", (user_data['user_id'], amount, datetime.now(),descrip))

            conn.commit()

            cursor.execute("select balance from accounts where user_id = %s",(user_data['user_id'],))
            balancefetch = cursor.fetchone() 
            session['user'] = {**user_data, 'balance' : balancefetch[0]}
            print(session['user'])

            cursor.close()

            conn.close()

            flash("Funds deposited successfully!")

            return redirect(url_for('dashboard'))

        return render_template("deposit.html",user_data=user_data)

    else:

        return redirect(url_for('login'))


#-----------------------Statement----------------------
    
@app.route('/statement' , methods=['POST','GET'])
def renderStatement():
    
    user_data = session['user']

    if user_data : 
        conn = get_db_connection() 
        print("connection made")
        cursor = conn.cursor() 
        cursor.execute("Select * from account_statements where user_id = %s",(user_data['user_id'],))
        statements = cursor.fetchall() 
        print(statements)
        cursor.close() 
        conn.close()
    else:
        return redirect(url_for('login'))

    return render_template("statements.html",user_data = user_data,statements = statements)


#---------------------------transfer---------------------

@app.route("/transfer", methods=['post', 'get' ])
def transfer():
    user_data = session.get('user')
    if user_data:
        if request.method == 'POST':
            rec_id = request.form.get('recipient_id')
            amount = request.form.get('amount')

            if rec_id and amount:
                try:
                    amount = float (amount)
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (rec_id, ))
                    recipient_user_id = cursor.fetchone()

                    if recipient_user_id is None:
                        flash("Recipient user not found!")
                        return redirect(url_for('transfer'))

                    # Check if the sender has sufficient balance
                    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
                    sender_balance = cursor.fetchone()

                    if sender_balance is None:
                        flash("Sender account not found!")
                        return redirect(url_for('transfer'))

                    sender_balance = sender_balance[0]

                    if sender_balance >= amount:
                        # sender 
                        
                        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id = %s", (amount, user_data['user_id']))

                        # Update recipient's balance
                        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s", (amount, recipient_user_id[0]))

                        # Insert a new transaction into the account_statements table
                        desc = request.form.get('description') 
                        cursor.execute("INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date,description) VALUES (%s, 'Debit', %s, %s ,%s)", (user_data['user_id'], amount, datetime.now( ),desc) )
                        cursor.execute("INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date,description) VALUES (%s, 'Credit', %s, %s,%s)", (recipient_user_id[0], amount, datetime.now(),desc))

                        session['user'] = {**user_data , 'balance' : user_data['balance'] - amount}

                        conn.commit()
                        cursor.close()
                        conn.close()
                        flash("Funds transferred successfully!")
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Insufficient balance!")
                        return redirect(url_for('transfer'))
                except ValueError:
                    flash("Invalid transfer amount!")
                    return redirect(url_for('transfer'))

            else:
                flash("Please fill in all fields!")
                return redirect(url_for('transfer'))
        return render_template("transfer.html",user_data=user_data)
    else:
        return redirect(url_for('login'))
    
#----- balance -----------------------
    
@app.route("\balance")
def renderBalance():
    user_data = session['user']
    return render_template('balance.html',user_data = user_data)

if __name__=='__main__':
    app.run(debug=True) 