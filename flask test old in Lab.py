from flask import Flask, render_template

app = Flask(__name__)

@app.route("/a")
def sayHi():
    print("Hiiiiiiii")
    return "Bye"

@app.route("/")
def runIndex():
    return render_template("index.html")

@app.route('/homPageee')
def nextLink():
    return render_template("homPage.html")

if __name__=='__main__':
    app.run(debug=True)