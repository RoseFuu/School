from flask import Flask, render_template

auth = Flask(__name__)


@auth.route("/")
def hello_world():
    return render_template("index.html")
