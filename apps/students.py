from flask import Blueprint, render_template, request, redirect,session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename


students = Blueprint("students", __name__)
conn = sqlite3.connect('data.sqlite', check_same_thread=False)


@students.route("/")
def home():
    if 'logedin' not in session:
        return redirect("/")
    current_url = ("/students")
    conn.row_factory = sqlite3.Row
    sqlStudentTable = "SELECT students.* ,classes.name as classes_name FROM students LEFT JOIN classes ON students.classroom = classes.id"
    dataStudent = conn.execute(sqlStudentTable).fetchall()
    return render_template("/students/index.html", dataStudent=dataStudent, current_url=current_url)


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@students.route("/add", methods=['GET', 'POST'])
def add_student():
    current_url = "/add"
    if 'logedin' not in session:
        return redirect("/")
    if request.method == 'GET':
        conn.row_factory = sqlite3.Row
        sqlClassOption = "SELECT * FROM classes"
        dataClass = conn.execute(sqlClassOption).fetchall()
        return render_template("/students/add.html", dataClass=dataClass, current_url=current_url)
    else:
        data_post = request.form
        name = data_post["name"]
        classroom = data_post["classroom"]
        age = int(data_post["age"])
        address = data_post["address"]
        telephone = data_post["telephone"]
        email = data_post["email"]
        error = None
        if age !="":
            if age >= 16 and age < 80:
                pass
            else:
                error = "Độ Tuổi Không Phù Hợp Xin Hãy Nhập Lại"
        if telephone != "":
            if "0" == telephone[0] and len(telephone) == 10:
                sqlCheckTelephone = "SELECT * FROM students WHERE telephone = '"+str(telephone)+"'"
                dataTelephone = conn.execute(sqlCheckTelephone).fetchall()
                if dataTelephone:
                    error = "Đã Có Số Điện Thoại"
            else:
                error = "Sai Format Telephone Xin Hãy Nhập Lại"
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/students")
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join('C:\Projects\School',
                                     'static', 'uploads', filename)
            if os.path.isfile(full_path):
                import time
                ts = time.time()
                filename = str(ts) + "_" + filename
                full_path = os.path.join('C:\Projects\School',
                                         'static', 'uploads', filename)
            file.save(full_path)        
        if error:
            sqlClassOption = "SELECT * from classes"
            dataClass = conn.execute(sqlClassOption).fetchall()
            return render_template("students/add.html", data = {'name':name,'classroom':classroom ,'age': age, 'address' : address, 'telephone' : telephone, 'email' : email}, error = error, dataClass = dataClass)
        sqlAddStudent = "INSERT INTO students (name,classroom,age,address,telephone,email,img) VALUES('"+str(
            name)+"','"+str(classroom)+"','"+str(age)+"','"+str(address)+"','"+str(telephone)+"','"+str(email)+"','"+str(filename)+"')"
        conn.execute(sqlAddStudent)
        conn.commit()
        return redirect("/students")
    

@students.route('/edit/<id_student>',methods = ['GET','POST'])
def edit_student(id_student):
    conn.row_factory = sqlite3.Row
    if 'logedin' not in session:
        return redirect("/")
    if int(id_student) > 0 :
        if request.method == 'GET':
            sqlSelectStudent = "SELECT * FROM students WHERE id = '"+str(id_student)+"'"
            dataStudent = conn.execute(sqlSelectStudent).fetchone()
            sqlClassOption = "SELECT * from classes"
            dataClass = conn.execute(sqlClassOption).fetchall()
            return render_template("students/edit.html", data = dataStudent, dataClass = dataClass)
        else:
            data_post = request.form
            name = data_post["name"]
            classroom = data_post["classroom"]
            age = int(data_post["age"])
            address = data_post["address"]
            telephone = data_post["telephone"]
            email = data_post["email"]
            sqlcheckFile = "SELECT * FROM students WHERE id = "+str(id_student)
            data_file = conn.execute(sqlcheckFile).fetchone()
            file = request.files['file']
            print(data_file['img'])
            if file and allowed_file(file.filename):
                if str(data_file['img']) != "" and os.path.exists('C:\\Projects\\School\\static\\uploads\\' + str(data_file['img'])) :
                    os.remove('C:\\Projects\\School\\static\\uploads\\' + str(data_file['img']))
                filename = secure_filename(file.filename)
            full_path = os.path.join('C:\Projects\School',
                                     'static', 'uploads', filename)
            if os.path.isfile(full_path):
                import time
                ts = time.time()
                filename = str(ts) + "_" + filename
                full_path = os.path.join('C:\Projects\School',
                                         'static', 'uploads', filename)
            file.save(full_path)
            sqlUpdateStudent = "UPDATE students SET name = '"+ str(name) +"',classroom = '"+ str(classroom) +"', age = '"+ str(age) +"' , address ='" + str(address) + "',telephone = '"+str(telephone)+"', email = '"+str(email)+"' , img = '"+str(filename)+"' WHERE id="+str(id_student)
            conn.execute(sqlUpdateStudent)
            conn.commit()
            return redirect("/students")
        
        
@students.route('/delete/<id_student>')
def delete_student(id_student):
    if 'logedin' not in session:
        return redirect("/")
    if int(id_student) > 0:
        sqlDeleteStudent = "DELETE FROM students where id = '"+str(id_student)+"'"
        conn.execute(sqlDeleteStudent)
        conn.commit()
        return redirect("/students")        
    
        
@students.route('/check-available-email', methods=['POST'])
def email_available():
    params = request.form
    if "id" in params and int(params["id"]) > 0 :
        sqlCheckEmail = "SELECT * FROM students WHERE email = '"+str(params['email'])+"' AND id != '"+str(params["id"])+"' "
    else :    
        sqlCheckEmail = "SELECT * FROM students WHERE email = '"+str(params['email'])+"'"
    dataEmail = conn.execute(sqlCheckEmail).fetchone()
    if dataEmail is None:
        return "true"
    else:
        return "false"

