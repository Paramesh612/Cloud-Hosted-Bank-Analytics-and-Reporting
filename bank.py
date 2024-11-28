import hashlib
from flask import *
import mysql.connector 
from datetime import datetime


app= Flask(__name__)
app.secret_key = "your_secret_key"

# Database config #---------------------------------------------------------------------------------------------------------
# db_config = {
#     'host': 'localhost', #bank.crqmssgockvo.ap-south-1.rds.amazonaws.com
#     'user': 'root',
#     'password': '',
#     'database': 'AWS_Bank'
# }

db_config = {
    'host': 'aws-bank-id.cinhykomuoh0.us-east-1.rds.amazonaws.com', #bank.crqmssgockvo.ap-south-1.rds.amazonaws.com
    'user': 'admin',
    'password': 'abcdefg123',
    'database': 'aws_bank'
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

        cursor.execute("select balance from accounts where user_id = %s and account_type = 'Savings' ",(user['user_id'],))
        savbal = cursor.fetchone() 
    
        cursor.execute("select balance from accounts where user_id = %s and account_type = 'Business'",(user['user_id'],))
        curbal = cursor.fetchone()

        try:
            print("Sav Cur Bal Before:")
            print(savbal , curbal)

            if savbal :
                session["user"] = {**user, 'savbalance': savbal['balance']}

            if curbal:  
                session["user"] = {**user, 'curbalance': curbal['balance']}

            if savbal and curbal:
                session["user"] = {**user, 'savbalance': savbal['balance'] ,'curbalance': curbal['balance']}



        except Exception as e:
            print("SavlBal CurBal Error: ",e)

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

#-----------dashboard---------------------------------
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


#------------deposit------------------

@app.route("/deposit", methods=['post', 'get'])

def deposit():

    #print(session)  # Check the contents of the session
    user_data = session.get('user')
    #print(user_data)

    if user_data:

        if request.method == 'POST':

            amount = float(request.form['deposit_amount'])

            account_type = request.form['account_type']

            descrip = request.form['desc']

            conn = get_db_connection()

            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM accounts WHERE user_id = %s and account_type=%s ", (user_data['user_id'],account_type))

            if not cursor.fetchone():

                # Insert a new row

                cursor.execute("INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)", (user_data['user_id'], amount, account_type))

                cursor.execute("INSERT INTO account_statements (user_id, account_type ,transaction_type,transaction_amount, transaction_date,description) VALUES (%s, %s ,'Credit', %s, %s,%s)", (user_data['user_id'],account_type, amount, datetime.now(),descrip))

            else:

                # Update the existing row

                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE ( user_id = %s and account_type = %s )", (amount, user_data['user_id'],account_type))

                cursor.execute("INSERT INTO account_statements (user_id, account_type, transaction_type,transaction_amount,  transaction_date,description) VALUES (%s, %s, 'Credit', %s, %s,%s)", (user_data['user_id'],account_type, amount, datetime.now(),descrip))

            conn.commit()

            #cursor.execute("select balance from accounts where user_id = %s",(user_data['user_id'],))
            #balancefetch = cursor.fetchone()
            
            # cursor.execute("select balance from accounts where user_id = %s and account_type = 'Savings' ",(user_data['user_id'],))
            # savbal = cursor.fetchone() 
            # cursor.execute("select balance from accounts where user_id = %s and account_type = 'Business'",(user_data['user_id'],))
            # curbal = cursor.fetchone() 

            updateBalanceInSession()
                        
            # print(session['user'])
            # if curbal and savbal:
            #     session['user'] = {
            #         **user_data, 
            #         'savbalance' : savbal[0], 
            #         'curbalance': curbal[0]
            #     }
            # elif curbal:
            #     session['user'] = {**user_data, 'curbalance': curbal[0]}
            # elif savbal:
            #     session['user'] = {**user_data, 'savbalance' : savbal[0]}


            print(session['user'])

            cursor.close()

            conn.close()

            flash("Funds deposited successfully!")

            return redirect(url_for('dashboard'))

        print("Session:",session['user'])
        print("\n\nUser Data:\n ", user_data)

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
        cursor = conn.cursor(dictionary=True) 
        cursor.execute("Select * from account_statements where user_id = %s",(user_data['user_id'],))
        statements = cursor.fetchall()
        # print(statements)
        cursor.close() 
        conn.close()
    else:
        return redirect(url_for('login'))

    return render_template("statements.html",user_data = user_data,statements = statements)


#---------------------------transfer------------------------------------------------------------------------------------

@app.route("/transfer", methods=['post', 'get' ])
def transfer():
    user_data = session.get('user')
    print(user_data)

    print("This is: ")

    if user_data:
        print("Inside User data")
        if request.method == 'POST':
            rec_id = request.form.get('recipient_id')
            amount = request.form.get('amount')
            sender_account_type = request.form.get('sender_account_type')
            receiver_account_type = request.form.get('rec_account_type')

            if rec_id and amount:
                try:
                    amount = float (amount)
                    conn = get_db_connection()
                    print("db connection made in transfer")
                    cursor = conn.cursor(buffered=True)
                    print("cursor.........................") 
                    print(user_data)
                    try:
                        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (rec_id,)) 
                        print("User Id fetched for transfer")
                    except Exception as e: 
                        print(e)

                   
                    recipient_user_id = cursor.fetchone()

                    if recipient_user_id is None:
                        flash("Recipient user not found!")
                        return redirect(url_for('transfer'))

                    # Check if the sender has sufficient balance
                    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s and account_type =%s", (user_data['user_id'],sender_account_type) ) 
                    sender_balance = cursor.fetchone()

                    if sender_balance is None or sender_balance[0]<=0:
                        flash("Sender account not found!")
                        return redirect(url_for('transfer'))

                    sender_balance = sender_balance[0]

                    if sender_balance >= amount:
                        # sender 
                        try:
                            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id = %s and account_type = %s", (amount, user_data['user_id'] , sender_account_type))
                            # Update recipient's balance
                            # print(IntegerRecepientId)
                            
                            IntegerRecepientId = recipient_user_id[0]

                            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE user_id = %s and account_type = %s", (amount, IntegerRecepientId , receiver_account_type))
                            
                            print("execting brother ")
                            # Insert a new transaction into the account_statements table
                            desc = request.form.get('description') 
                            
                            try:
                                cursor.execute("INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date,description,from_account_id,to_account_id) VALUES (%s, 'Debit', %s, %s ,%s,%s,%s)", (user_data['user_id'], amount, datetime.now(),desc,user_data['user_id'] , IntegerRecepientId ))
                                cursor.execute("INSERT INTO account_statements (user_id, transaction_type, transaction_amount, transaction_date,description,from_account_id,to_account_id) VALUES (%s, 'Credit', %s, %s,%s,%s,%s)", (IntegerRecepientId, amount, datetime.now(),desc,user_data['user_id'] , IntegerRecepientId))
                            except Exception as e:
                                print("New Error:",e)

                            try:
                                # newBal = float(user_data['savbalance']) - amount
                                # newBalCur = float(user_data['curbalance']) - amount
                                # session['user'] = {
                                #     **user_data , 
                                #     'savbalance' : newBal , 
                                #     'curbalance' : newBalCur 
                                # }

                                updateBalanceInSession()

                                print(session['user'])
                            except Exception as e:
                                print("Setting Session Error: ",e) 

                            try:
                                conn.commit()
                                cursor.close()
                                conn.close()
                            except Exception as e:
                                print("Closing Error: ",e)

                            print("Funds transferred successfully!")

                        except Exception as e:
                            print("Error for updating: ",e)

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
    
@app.route("/balance")
def renderBalance():
    user_data = session['user']
    print(user_data)
    return render_template('balance.html',user_data = user_data)


#----------account creation--------------------------

@app.route("/account-creation")
def renderAccCreation():
    user_data = session['user']
    return render_template("account_creation.html",user_data=user_data)

#-----------------------------------------------

def updateBalanceInSession():
    user_data = session['user']
    conn = get_db_connection()
    curr=conn.cursor()

    curr.execute("select balance from accounts where user_id = %s and account_type = 'Savings' ",(user_data['user_id'],))
    savbal = curr.fetchone() 
    curr.execute("select balance from accounts where user_id = %s and account_type = 'Business'",(user_data['user_id'],))
    curbal = curr.fetchone() 

    if savbal:
        session['user'].update({ 'savbalance': savbal[0] })
    if curbal:
        session['user'].update({ 'curbalance' : curbal[0] })



#-----------------------main---------------------
if __name__=='__main__':
    app.run(debug=True) 