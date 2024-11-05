from flask import Flask, render_template

app= Flask(__name__)

@app.route('/')
def renderHome():
    return render_template("index2.html")

@app.route('/register')
def renderRegister():
    return render_template("register.html")

@app.route('/login')
def renderLogin():
    return render_template("login.html")


@app.route('/dashboard')
def renderDashboard():
    return render_template("dashboard.html")

if __name__=='__main__':
    app.run(debug=True) 