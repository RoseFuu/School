from flask import Flask, render_template, Blueprint, redirect, session
from flask_session import Session
from apps.students import students
from apps.teachers import teachers
from apps.classes import classes
from apps.auth import auth

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def default():
    if 'logedin' in session:
        return redirect("/students")
    else:
        return redirect("/auth/login")


app.register_blueprint(students, url_prefix="/students")
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(teachers, url_prefix="/teachers")
app.register_blueprint(classes, url_prefix="/classes")
