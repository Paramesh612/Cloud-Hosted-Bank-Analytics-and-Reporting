from flask import Flask, render_template

app= Flask(__name__)

@app.route('/')
def renderHome():
    return render_template("index2.html")

@app.route('/login')
def renderLogin():
    return render_template("index2.html")

if __name__=='__main__':
    app.run(debug=True) 