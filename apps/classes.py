from flask import Blueprint, render_template, request, redirect, session, jsonify
import sqlite3

classes = Blueprint("classes", __name__)
conn = sqlite3.connect('data.sqlite', check_same_thread=False)


@classes.route("/")
def home():
    if 'logedin' not in session:
        return redirect("/")
    conn.row_factory = sqlite3.Row
    current_url = "/classes"
    sqlClassQuery = "SELECT classes.*,teachers.name as teachers_name FROM classes LEFT JOIN teachers ON classes.id_teacher = teachers.id "
    dataClasses = conn.execute(sqlClassQuery).fetchall()
    return render_template("classes/index.html", dataClasses=dataClasses, current_url=current_url)


@classes.route("/add", methods=["GET", "POST"])
def add_class():
    if 'logedin' not in session:
        return redirect("/")
    current_url = "/classes/add"
    if request.method == "GET":
        sqlTeacherOption = "SELECT * FROM teachers"
        conn.row_factory = sqlite3.Row
        dataTeacher = conn.execute(sqlTeacherOption).fetchall()
        return render_template("classes/add.html", current_url=current_url, teachers=dataTeacher)
    else:
        data_post = request.form
        name = data_post["name"]
        formteacher = data_post["formteacher"]
        sqlAddClass = "INSERT INTO classes ({}) VALUES ({})".format(
            "name,id_teacher", +str(name) + str(formteacher))
        print(sqlAddClass)
        conn.execute(sqlAddClass)
        conn.commit()
        return redirect("/classes")


@classes.route("/edit/<id_classes>", methods=['GET', 'POST'])
def edit_classes(id_classes):
    if 'logedin' not in session:
        return redirect("/")
    if int(id_classes) > 0:
        if request.method == "GET":
            sqlSelectClasses = "SELECT classes.*,teachers.name as teachers_name FROM classes LEFT JOIN teachers ON classes.id_teacher = teachers.id WHERE classes.id = " + \
                str(id_classes)
            dataClasses = conn.execute(sqlSelectClasses).fetchone()
            return render_template("classes/edit.html", data=dataClasses)
        else:
            data_post = request.form
            name = data_post["name"]
            sqlUpdateClasses = "UPDATE classes SET name = '" + \
                str(name)+"' WHERE id = "+str(id_classes)
            conn.execute(sqlUpdateClasses)
            conn.commit()
            return redirect("/classes")
    else:
        return "/"


@classes.route("/delete/<id_classes>/<step>", methods=['POST'])
def delete_classes(id_classes, step=0):
    if 'logedin' not in session:
        return redirect("/")
    if int(id_classes) > 0:
        if int(step) == 1:
            sqlCheckStudentInClass = "SELECT * FROM students WHERE id = '" + \
                str(id_classes)+"'"
            dataClass = conn.execute(sqlCheckStudentInClass).fetchall()
            if len(dataClass) > 0:
                return jsonify({'status': "ok", 'step': 1, 'current_class_id': id_classes, 'has_student': 1})
            else:
                return jsonify({'status': "faild", 'step': 1, 'current_class_id': id_classes, 'has_student': 0})
        elif int(step) == 2:
            form_data = request.form
            if "has_student" in form_data:
                if int(form_data["has_student"]) == 1:
                    sqlUpdateStudent = "UPDATE students SET classes = {} WHERE classes = {}".format(
                        form_data["new_id"], id_classes)
                    conn.execute(sqlUpdateStudent)
                    conn.commit()
            sqlDeleteClasses = "DELETE FROM classes WHERE id = '{}'".format(
                id_classes)
            conn.execute(sqlDeleteClasses)
            conn.commit()
            return jsonify({'status': "ok", 'step': 2})
    else:
        result = {
            "status": "faild",
            "message": "Ban vui long gui id > 0"
        }
        return jsonify(result)


@classes.route("/manager/<id_classes>")
def manager(id_classes):
    if int(id_classes) > 0:
        conn.row_factory = sqlite3.Row
        sqldataClass = "SELECT * FROM classes where  id = '" + \
            str(id_classes)+"' "
        dataClass = conn.execute(sqldataClass).fetchone()
        sqlShowTeacher = "SELECT * FROM teachers"
        dataTeacher = conn.execute(sqlShowTeacher).fetchall()
        sql_query_list_teacher_status = "SELECT * FROM teacher_class where id_class={}".format(
            id_classes)
        list_teacher_on_class = conn.execute(
            sql_query_list_teacher_status).fetchall()
        list_teacher_avaiable = []
        for x in list_teacher_on_class:
            list_teacher_avaiable.append(x["id_teacher"])
        dataresult = []
        for x in dataTeacher:
            teacher = {}
            teacher['id'] = x["id"]
            teacher['name'] = x["name"]
            teacher['subject'] = x["subject"]
            if x["id"] in list_teacher_avaiable:
                teacher['status'] = 1
            else:
                teacher['status'] = 0
            dataresult.append(teacher)

        return render_template("classes/manager_teacher.html", dataTeacher=dataresult, id_classes=id_classes, dataClass=dataClass)


@classes.route("/manager/teacher", methods=['POST'])
def uploads():
    data = request.form
    result = {
        'status': 0,
        'newtext': "Thêm",
        'newstatus': "Không Dạy"
    }
    if int(data["status"]) == 0:
        sql = "INSERT INTO teacher_class  (id_teacher,id_class) VALUES ({},{})".format(
            data["teacher"], data["class_id"])
        conn.execute(sql)
        conn.commit()
        result['status'] = 1
        result['newtext'] = "Gỡ"
        result['newstatus'] = "Đang Dạy"
    else:
        sql = "DELETE FROM teacher_class WHERE id_teacher = {} AND id_class = {}".format(
            data["teacher"], data["class_id"])
        conn.execute(sql)
        conn.commit()
    return jsonify(result)
