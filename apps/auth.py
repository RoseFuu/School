from flask import Blueprint, render_template, request, redirect, session
import sqlite3

auth = Blueprint('auth', __name__)
conn = sqlite3.connect('data.sqlite', check_same_thread=False)


@auth.route('/')
def default_login():
    return redirect('/auth/login')


@auth.route('/login', methods=["POST", "GET"])
def login():
    if 'logedin' in session:
        return redirect("/")
    if request.method == "GET":
        paramater = request.args
        error = None
        if "error" in paramater:
            error = "Tài Khoản Không Tồn Tại"
        return render_template("login.html", error=error)

    else:
        data_form = request.form
        email = data_form['email']
        password = data_form['password']
        if email is None or password is None:
            return "error"
        else:
            sqlAdminTable = "SELECT * FROM admin WHERE name = '" + \
                str(email)+"' AND password = '"+str(password)+"'"
            dataAdmin = conn.execute(sqlAdminTable).fetchone()
            if dataAdmin is None:
                return redirect("/auth/login?error=1")
            else:
                session['email'] = email
                session['logedin'] = True
                return redirect("/")


@auth.route("/logout")
def logout():
    if 'logedin' in session:
        session.clear()
        return redirect("/")
