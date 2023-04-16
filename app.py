from flask import Flask, render_template, request, redirect
import json;
from flaskext.mysql import MySQL
import os
from werkzeug.utils import secure_filename
import random
import string

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jen@2004'
app.config['MYSQL_DATABASE_DB'] = 'ums'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'static/css'
mysql.init_app(app)


@app.route("/")
def index():
    return "hello world from flask-Application"

@app.route("/addmisionForm")
def addmisionForm():
    return render_template('addmisionForm2.html');

@app.route("/fetchCity")
def fetchCity():
    connection  = mysql.connect()
    cursor      = connection.cursor()

    cursor.execute('Select * from city');
    citiesDb = cursor.fetchall();
    connection.close();

    col = ['cityID', 'city'];
    cities = []
    for i in citiesDb:
        cities.append(dict(zip(col, i)));

    return json.dumps(cities);

@app.route('/fetchDegree')
def fetchDegree():
    connection  = mysql.connect();
    cursor      = connection.cursor();

    cursor.execute('select * from Degree');
    degreesDB = cursor.fetchall();
    connection.close();

    degrees = [];
    col = ['degreeID', 'degree'];
    for degree in degreesDB:
        degrees.append( dict(zip(col, degree)));

    return json.dumps(degrees);

@app.route('/fetchCourse/<degreeID>')
def fetchCourse(degreeID):
    connection  = mysql.connect();
    cursor      = connection.cursor();

    cursor.execute(f'select * from courses where degreeId = {degreeID}');
    coursesDB = cursor.fetchall();
    connection.close();

    col = ['courseID', 'course'];
    courses = []
    for course in coursesDB:
        courses.append(dict(zip( col, course )));

    return json.dumps(courses);

@app.route('/fetchAddmisionQuta')
def fetchAddmisionQuta():
    connection  = mysql.connect();
    cursor      = connection.cursor();

    cursor.execute('select * from AddmissionQuataFields');
    qutasDB = cursor.fetchall();
    connection.close();

    col = ['qutaID', 'quta'];
    qutas = [];
    for quta in qutasDB:
        qutas.append( dict(zip( col, quta )));

    return json.dumps(qutas);


@app.route('/registerStudent', methods=['get','post'])
def registerStudent():
    firstName   = request.form.get('firstName');
    middleName  = request.form.get('middleName');
    lastName    = request.form.get('lastName');
    addharNo    = request.form.get('aadharNo');
    print(addharNo);
    gender      = request.form.get('gender');
    cityID      = int(request.form.get('cityID'));
    degreeID    = int(request.form.get('degreeID'));
    courseID    = int(request.form.get('courseID'));
    qutaID      = int(request.form.get('qutaID'));
    contact_no1 = request.form.get('contact-no1');
    contact_no2 = request.form.get('contact-no2');
    contact     = [contact_no1, contact_no2];
    photo       = request.files['photo'];
    photoName   = secure_filename(photo.filename);
    
    try:
        connection  = mysql.connect();
        cursor      = connection.cursor();

        for number in contact:
            cursor.execute(f"Insert into contactDetails (contactNo) values ('{number}')");

        if photoName != None:
            photoPath = 'static/students/'+photoName;
            photo.save(photoPath);
            cursor.execute(f"Insert into studentDetails (firstName, middleName, lastName, addharNo, gender, cityID, degreeID, courseID, photoPath) values ('{firstName}', '{middleName}','{lastName}', '{addharNo}', '{gender}', {cityID}, {degreeID}, {courseID}, '{photoPath}')");
        else:
            cursor.execute(f"Insert into studentDetails (firstName, middleName, lastName, addharNo, gender, cityID, degreeID, courseID) values ('{firstName}', '{middleName}','{lastName}', '{addharNo}', '{gender}', {cityID}, {degreeID}, {courseID})");


        cursor.execute("select max(SID) from studentDetails");
        SID = cursor.fetchall()[0][0];

        if(SID == None or SID == 0):
            print(SID);
            SID = 1;

        for contactNo in contact:
            print(contactNo);
            if contactNo != '' or contactNo != None:
                cursor.execute(f"insert into studentWiseContact (contactId, SID) select contactID, {SID} from ContactDetails where ContactNo = '{contactNo}'");

        cursor.execute(f"Insert into addmisionDetails (SID, QutaId, courseId, date, year) values ({SID},{qutaID}, {courseID}, curdate(), year(curdate()))");

        password = ''
        for i in range(6):
            password += random.choice(string.ascii_letters + string.digits);

        cursor.execute(f"Insert into loginPassword (userID, password, designation) values ('{contact_no1}', '{password}', 'student')")
        cursor.execute(f"update studentDetails set userID = '{contact_no1}' where SID = {SID}")
        connection.commit();
        
    except Exception as e:
        print("Exception : ", e);

    finally:
        connection.close();
    

    return redirect("/addmisionForm");

@app.route('/login', methods=['post','get'])
def login():
    print(request.method)
    if request.method == 'GET':
        print('hello');
        return render_template('loginForm.html');

    elif request.method == 'POST':
        userID = request.form.get('userID');
        password = request.form.get('password');
        
        connection  = mysql.connect();
        cursor      = connection.cursor();

        cursor.execute(f"select password, designation from loginPassword where userID = '{userID}'");
        response = cursor.fetchall();
        passwordDB  = response[0][0];
        designation = response[0][1];

        if(password == None or password == ''):
            return 'type password';
        elif password != passwordDB:
            return 'wrongPassword'
        elif(password == passwordDB):
            return 'student';

    return render_template('loginForm.html');

@app.route('/login1', methods = ['post'])
def login1():
    userID = request.form.get('userID');
    password = request.form.get('password');

    connection  = mysql.connect();
    cursor      = connection.cursor();

    cursor.execute(f"select password, designation from loginPassword where userID = '{userID}'");
    response = cursor.fetchall();
    passwordDB  = response[0][0];
    designation = response[0][1];

    if(password == None or password == ''):
        return 'wrongPassword';
    elif(password == passwordDB):
        return 'student';

    return 'hello successfull'



@app.route('/p')
def p():
    return render_template('photo.html');

