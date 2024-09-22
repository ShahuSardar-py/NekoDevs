from flask import Flask, render_template, request

app= Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/app")
def home2():
    return render_template("dashboard2.html")


if __name__=="__main__":
    app.run(debug=True)