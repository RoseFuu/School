from flask import Blueprint, render_template, request, redirect, session
import sqlite3

teachers = Blueprint("teachers", __name__)
conn = sqlite3.connect('data.sqlite', check_same_thread=False)


@teachers.route("/")
def home():
    if 'logedin' not in session:
        return redirect("/")
    current_url = ("/teachers")
    conn.row_factory = sqlite3.Row
    sqlTeacherTable = "SELECT teachers.* ,classes.name as classes_name FROM teachers LEFT JOIN classes ON teachers.classroom = classes.id"
    dataTeacher = conn.execute(sqlTeacherTable).fetchall()
    return render_template("/teachers/index.html", dataTeacher=dataTeacher, current_url=current_url)

@teachers.route("/add", methods=['GET', 'POST'])
def add_student():
    current_url = "/teachers/add"
    if 'logedin' not in session:
        return redirect("/")
    if request.method == 'GET':
        conn.row_factory = sqlite3.Row
        sqlClassOption = "SELECT * FROM classes"
        dataClass = conn.execute(sqlClassOption).fetchall()
        return render_template("/teachers/add.html", dataClass=dataClass, current_url=current_url)
    else:
        data_post = request.form
        name = data_post["name"]
        classroom = data_post["classroom"]
        age = int(data_post["age"])
        address = data_post["address"]
        telephone = data_post["telephone"]
        email = data_post["email"]
        subject = data_post["subject"]
        error = None
        if age !="":
            if age >= 18 and age < 80:
                pass
            else:
                error = "Độ Tuổi Không Phù Hợp Xin Hãy Nhập Lại"
        if telephone != "":
            if "0" == telephone[0] and len(telephone) == 10:
                sqlCheckTelephone = "SELECT * FROM teachers WHERE telephone = '"+str(telephone)+"'"
                dataTelephone = conn.execute(sqlCheckTelephone).fetchall()
                if dataTelephone:
                    error = "Đã Có Số Điện Thoại"
            else:
                error = "Sai Format Telephone Xin Hãy Nhập Lại"
        if error:
            sqlClassOption = "SELECT * from classes"
            dataClass = conn.execute(sqlClassOption).fetchall()
            return render_template("teachers/add.html", data = {'name':name,'classroom':classroom ,'age': age, 'address' : address, 'telephone' : telephone, 'email' : email, 'subject':subject}, error = error, dataClass = dataClass)
        sqlAddStudent = "INSERT INTO teachers (name,classroom,age,address,telephone,email,subject) VALUES('"+str(
            name)+"','"+str(classroom)+"','"+str(age)+"','"+str(address)+"','"+str(telephone)+"','"+str(email)+"','"+str(subject)+"')"
        conn.execute(sqlAddStudent)
        conn.commit()
        return redirect("/teachers")
    
@teachers.route('/edit/<id_teacher>',methods = ['GET','POST'])
def edit_student(id_teacher):
    if 'logedin' not in session:
        return redirect("/")
    if int(id_teacher) > 0 :
        if request.method == 'GET':
            conn.row_factory = sqlite3.Row
            sqlSelectTeacher = "SELECT * FROM teachers WHERE id = '"+str(id_teacher)+"'"
            dataTeacher = conn.execute(sqlSelectTeacher).fetchone()
            sqlClassOption = "SELECT * from classes"
            dataClass = conn.execute(sqlClassOption).fetchall()
            return render_template("teachers/edit.html", data = dataTeacher, dataClass = dataClass)
        else:
            data_post = request.form
            name = data_post["name"]
            classroom = data_post["classroom"]
            age = int(data_post["age"])
            address = data_post["address"]
            telephone = data_post["telephone"]
            email = data_post["email"]
            subject = data_post["subject"]
            sqlUpdateTeacher = "UPDATE teachers SET name = '"+ str(name) +"',classroom = '"+ str(classroom) +"', age = '"+ str(age) +"' , address ='" + str(address) + "',telephone = '"+str(telephone)+"', email = '"+str(email)+"', subject = '"+str(subject)+"' WHERE id="+str(id_teacher)
            conn.execute(sqlUpdateTeacher)
            conn.commit()
            return redirect("/teachers")
        
@teachers.route('/delete/<id_teacher>')
def delete_teacher(id_teacher):
    if 'logedin' not in session:
        return redirect("/")
    if int(id_teacher) > 0:
        sqlDeleteTeacher = "DELETE FROM teachers where id = '"+str(id_teacher)+"'"
        conn.execute(sqlDeleteTeacher)
        conn.commit()
        return redirect("/teachers")       
    
@teachers.route('/check-available-email', methods=['POST'])
def email_available():
    params = request.form
    if "id" in params and int(params["id"]) > 0 :
        sqlCheckEmail = "SELECT * FROM teachers WHERE email = '"+str(params['email'])+"' AND id != '"+str(params["id"])+"' "
    else :    
        sqlCheckEmail = "SELECT * FROM teachers WHERE email = '"+str(params['email'])+"'"
    dataEmail = conn.execute(sqlCheckEmail).fetchone()
    if dataEmail is None:
        return "true"
    else:
        return "false"
