from datetime import datetime
import sqlite3
from datetime import date
from flask import Flask, request, render_template

# Определение Flask приложения
app = Flask(__name__)

# Код для SQLite 3

conn = sqlite3.connect('database/lifecare.db', check_same_thread=False)
c = conn.cursor()

# Создание таблиц
c.execute('''CREATE TABLE IF NOT EXISTS doctors(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            address text,
            doc_id integer text,
            password integer text,
            speciality text,
            status integer
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS patients(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            password integer text,
            address text,
            status integer
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS superusercreds(
            username integer text,
            password integer text
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS doctorappointmentrequests(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS doctorappointments(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
            )''')

# Инициализация суперпользователя
c.execute('SELECT * from superusercreds')
conn.commit()
adminuser = c.fetchall()
if not adminuser:
    c.execute("INSERT INTO superusercreds VALUES ('admin','admin')")
    conn.commit()


# Вспомогательные функции
def datetoday():
    today = datetime.now().strftime("%Y-%m-%d")
    return today


def checkonlyalpha(x):
    return x.isalpha()


def checkonlynum(x):
    return x.isdigit()


def checkpass(x):
    f1, f2, f3 = False, False, False
    if len(x) < 8:
        return False
    if any(c.isalpha() for c in x):
        f1 = True
    if any(c.isdigit() for c in x):
        f2 = True
    if any(c in x for c in ['@', '$', '!', '#', '%', '&', '*']):
        f3 = True

    return f1 and f2 and f3


def checkphnlen(x):
    return len(x) == 10


# Функции для работы с данными
def retalldocsandapps():
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    l = len(docsandapps)
    return docsandapps, l


def getpatdetails(phn):
    c.execute("SELECT * FROM patients WHERE phone_number=?", (phn,))
    conn.commit()
    patient = c.fetchone()
    return patient


def getdocdetails(docid):
    c.execute(f"SELECT * FROM doctors")
    conn.commit()
    doctors = c.fetchall()
    for i in doctors:
        if str(i[5]) == str(docid):
            return i


def retdocsandapps(docid):
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    docsandapps2 = []
    for i in docsandapps:
        if str(i[0]) == str(docid):
            docsandapps2.append(i)
    l = len(docsandapps2)
    return docsandapps2, l


def retapprequests(docid):
    c.execute(f"SELECT * FROM doctorappointmentrequests")
    conn.commit()
    appreq = c.fetchall()
    appreq2 = []
    for i in appreq:
        if str(i[0]) == str(docid):
            appreq2.append(i)
    l = len(appreq2)
    return appreq, l


def ret_patient_reg_requests():
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    patient_reg_requests = []
    for d in data:
        if str(d[-1]) == '0':
            patient_reg_requests.append(d)
    return patient_reg_requests


def ret_doctor_reg_requests():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    doctor_reg_requests = []
    for d in data:
        if str(d[-1]) == '0':
            doctor_reg_requests.append(d)
    return doctor_reg_requests


def ret_registered_patients():
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    registered_patients = []
    for d in data:
        if str(d[-1]) == '1':
            registered_patients.append(d)
    return registered_patients


def ret_registered_doctors():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    registered_doctors = []
    for d in data:
        if str(d[-1]) == '1':
            registered_doctors.append(d)
    return registered_doctors


def ret_docname_docspec():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docname_docid = []
    for i in registered_doctors:
        docname_docid.append(str(i[0]) + ' ' + str(i[1]) + '-' + str(i[5]) + '-' + str(i[7]))
    l = len(docname_docid)
    return docname_docid, l


def getdocname(docid):
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    for i in registered_doctors:
        if str(i[5]) == str(docid):
            return i[0] + '-' + i[1]


def getpatname(patnum):
    c.execute('SELECT * FROM patients')
    conn.commit()
    details = c.fetchall()
    for i in details:
        if str(i[3]) == str(patnum):
            return i[0] + ' ' + i[1]
    else:
        return -1


def get_all_docids():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docids = []
    for i in registered_doctors:
        docids.append(str(i[5]))
    return docids


def get_all_patnums():
    c.execute('SELECT * FROM patients')
    conn.commit()
    registered_patients = c.fetchall()
    patnums = []
    for i in registered_patients:
        patnums.append(str(i[3]))
    return patnums


# ОСНОВНЫЕ МАРШРУТЫ

# Главная страница
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/patreg')
def patreg():
    return render_template('patientregistration.html')


@app.route('/docreg')
def docreg():
    return render_template('doctorregistration.html')


@app.route('/loginpage1')
def loginpage1():
    return render_template('loginpage1.html')


@app.route('/loginpage2')
def loginpage2():
    return render_template('loginpage2.html')


@app.route('/loginpage3')
def loginpage3():
    return render_template('loginpage3.html')


# Регистрация пациентов
@app.route('/addpatient', methods=['POST'])
def addpatient():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    print(firstname, lastname, checkonlyalpha(firstname), checkonlyalpha(lastname))

    if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
        return render_template('home.html', mess=f'Имя и фамилия должны содержать только буквы')

    if not checkpass(passw):
        return render_template('home.html',
                               mess=f"Пароль должен быть длиной более 8 символов и содержать буквы, цифры и спецсимволы ('@','$','!')")

    if not checkphnlen(phn):
        return render_template('home.html', mess=f"Номер телефона должен содержать 11 цифр")

    if str(phn) in get_all_patnums():
        return render_template('home.html', mess=f'Пациент с номером {phn} уже существует')
    c.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, 0)",
              (firstname, lastname, dob, phn, passw, address))
    conn.commit()
    return render_template('home.html', mess=f'Запрос на регистрацию пациента {firstname} отправлен администратору')


# Регистрация врачей
@app.route('/adddoctor', methods=['GET', 'POST'])
def adddoctor():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.form['docid']
    spec = request.form['speciality']

    if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
        return render_template('home.html', mess=f'Имя и фамилия должны содержать только буквы')

    if not checkonlyalpha(spec):
        return render_template('home.html', mess=f'Специальность врача должна содержать только буквы')

    if not checkpass(passw):
        return render_template('home.html',
                               mess=f"Пароль должен быть длиной более 8 символов и содержать буквы, цифры и спецсимволы ('@','$','!')")

    if not checkphnlen(phn):
        return render_template('home.html', mess=f"Номер телефона должен содержать 11 цифр.")

    if str(docid) in get_all_docids():
        return render_template('home.html', mess=f'Врач с ID {docid} уже существует.')
    if str(phn) in get_all_patnums():  # Проверка на уникальность номера
        return render_template('home.html', mess=f'Номер {phn} уже зарегистрирован.')
    c.execute(
        f"INSERT INTO doctors VALUES ('{firstname}','{lastname}','{dob}','{phn}','{address}','{docid}','{passw}','{spec}',0)")
    conn.commit()
    return render_template('home.html', mess=f'Запрос на регистрацию врача {firstname} отправлен администратору.')


# Вход для пациентов
@app.route('/patientlogin', methods=['GET', 'POST'])
def patientlogin():
    phn = request.args.get('phn')
    if not phn:
        return render_template('patientlogin.html', mess="Номер телефона не указан")

    passw = request.form['pass']
    c.execute('SELECT * FROM patients')
    conn.commit()
    registerd_patients = c.fetchall()

    for i in registerd_patients:
        if str(i[3]) == str(phn) and str(i[4]) == str(passw):
            # Получение данных для отображения
            docsandapps, l = retalldocsandapps()
            docname_docid, l2 = ret_docname_docspec()

            # Формирование имён врачей для таблицы
            docnames = []
            for app in docsandapps:
                doc_name = getdocname(app[0])  # Получение имени врача по ID
                docnames.append(doc_name)

            # Получение имени пациента для приветствия
            pat_details = getpatdetails(phn)
            patname = f"{pat_details[0]} {pat_details[1]}" if pat_details else "Гость"

            return render_template('patientlogin.html',
                                   docsandapps=docsandapps,
                                   docnames=docnames,
                                   docname_docid=docname_docid,
                                   l=l,
                                   l2=l2,
                                   patname=patname,
                                   phn=phn,
                                   mess=f"Добро пожаловать, {patname}!")

    return render_template('loginpage1.html', err='Неверный телефон или пароль')

# Вход для врачей
@app.route('/doctorlogin', methods=['GET', 'POST'])
def doctorlogin():
    if request.method == 'POST':
        docid = request.form.get('docid')
        passw = request.form.get('pass')
    else:
        docid = request.args.get('docid')
        passw = None

    c.execute('SELECT * FROM doctors')
    conn.commit()
    registerd_doctors = c.fetchall()
    if request.method == 'POST':
        for i in registerd_doctors:
            if str(i[5]) == str(docid) and str(i[6]) == str(passw):
                appointment_requests_for_this_doctor, l1 = retapprequests(docid)
                fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
                return render_template('doctorlogin.html',
                                      appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                                      fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                                      l1=l1, l2=l2,
                                      docname=i[0],
                                      docid=docid)
        return render_template('loginpage2.html', err='Неверные учетные данные')

    # Если это GET-запрос (возврат с других страниц)
    elif request.method == 'GET' and docid:
        for i in registerd_doctors:
            if str(i[5]) == str(docid):
                appointment_requests_for_this_doctor, l1 = retapprequests(docid)
                fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
                return render_template('doctorlogin.html',
                                      appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                                      fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                                      l1=l1, l2=l2,
                                      docname=i[0],
                                      docid=docid)
        return render_template('loginpage2.html', err='Сессия устарела')
    else:
        return render_template('loginpage2.html', err='Требуется авторизация')


# Вход для администратора
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    username = request.form['username']
    passw = request.form['pass']
    c.execute('SELECT * FROM superusercreds')
    conn.commit()
    superusercreds = c.fetchall()

    for i in superusercreds:
        if str(i[0]) == str(username) and str(i[1]) == str(passw):
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminlogin.html', patient_reg_requests=patient_reg_requests,
                                   doctor_reg_requests=doctor_reg_requests, registered_patients=registered_patients,
                                   registered_doctors=registered_doctors, l1=l1, l2=l2, l3=l3, l4=l4)
    else:
        return render_template('loginpage3.html', err='Неверный логин или пароль.')


# Удаление пациентов
@app.route('/deletepatient', methods=['GET', 'POST'])
def deletepatient():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}' ")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminlogin.html', patient_reg_requests=patient_reg_requests,
                           doctor_reg_requests=doctor_reg_requests, registered_patients=registered_patients,
                           registered_doctors=registered_doctors, l1=l1, l2=l2, l3=l3, l4=l4)


# Удаление врачей
@app.route('/deletedoctor', methods=['GET', 'POST'])
def deletedoctor():
    docid = request.values['docid']
    c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}' ")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminlogin.html', patient_reg_requests=patient_reg_requests,
                           doctor_reg_requests=doctor_reg_requests, registered_patients=registered_patients,
                           registered_doctors=registered_doctors, l1=l1, l2=l2, l3=l3, l4=l4)


# Создание записи пациентом
@app.route('/makeappointment', methods=['GET', 'POST'])
@app.route('/makeappointment', methods=['POST'])
def makeappointment():
    try:
        # Получение данных
        phn = request.args.get('phn')
        appdate = request.form.get('appdate')
        whichdoctor = request.form.get('whichdoctor')

        # Проверка обязательных полей
        if not all([phn, appdate, whichdoctor]):
            return render_template('patientlogin.html',
                                   mess="Заполните все поля: врач и дата",
                                   phn=phn,
                                   docname_docid=ret_docname_docspec()[0],
                                   docsandapps=retalldocsandapps()[0],
                                   l=retalldocsandapps()[1],
                                   l2=ret_docname_docspec()[1]
                                   )

        # Проверка существования пациента
        patname = getpatname(phn)
        if patname == -1:
            return render_template('patientlogin.html',
                                   mess="Пациент не найден",
                                   phn=phn,
                                   docname_docid=ret_docname_docspec()[0],
                                   docsandapps=retalldocsandapps()[0],
                                   l=retalldocsandapps()[1],
                                   l2=ret_docname_docspec()[1]
                                   )

        # Извлечение ID врача из выбранного значения
        try:
            docid = whichdoctor.split('-')[-2].strip()  # Формат: "Имя Фамилия - ID - Специальность"
        except IndexError:
            return render_template('patientlogin.html',
                                   mess="Ошибка при выборе врача",
                                   phn=phn,
                                   docname_docid=ret_docname_docspec()[0],
                                   docsandapps=retalldocsandapps()[0],
                                   l=retalldocsandapps()[1],
                                   l2=ret_docname_docspec()[1]
                                   )

        # Проверка даты
        appdate_obj = datetime.strptime(appdate, '%Y-%m-%d').date()
        today = datetime.now().date()
        if appdate_obj <= today:
            return render_template('patientlogin.html',
                                   mess="Выберите дату",
                                   phn=phn,
                                   docname_docid=ret_docname_docspec()[0],
                                   docsandapps=retalldocsandapps()[0],
                                   l=retalldocsandapps()[1],
                                   l2=ret_docname_docspec()[1]
                                   )

        # Проверка существования врача
        if docid not in get_all_docids():
            return render_template('patientlogin.html',
                                   mess="Врач не найден",
                                   phn=phn,
                                   docname_docid=ret_docname_docspec()[0],
                                   docsandapps=retalldocsandapps()[0],
                                   l=retalldocsandapps()[1],
                                   l2=ret_docname_docspec()[1]
                                   )

        # Сохранение запроса в БД (безопасный запрос)
        c.execute('''
            INSERT INTO doctorappointmentrequests (docid, patientname, patientnum, appointmentdate)
            VALUES (?, ?, ?, ?)
        ''', (docid, patname, phn, appdate))
        conn.commit()

        return render_template('patientlogin.html',
                               mess="Запрос отправлен врачу",
                               phn=phn,
                               docname_docid=ret_docname_docspec()[0],
                               docsandapps=retalldocsandapps()[0],
                               l=retalldocsandapps()[1],
                               l2=ret_docname_docspec()[1]
                               )

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return render_template('patientlogin.html',
                               mess="Ошибка сервера. Попробуйте позже",
                               phn=phn,
                               docname_docid=ret_docname_docspec()[0],
                               docsandapps=retalldocsandapps()[0],
                               l=retalldocsandapps()[1],
                               l2=ret_docname_docspec()[1]
                               )


# Одобрение врача администратором
@app.route('/approvedoctor')
def approvedoctor():
    doctoapprove = request.values['docid']
    c.execute('SELECT * FROM doctors')
    conn.commit()
    doctor_requests = c.fetchall()
    for i in doctor_requests:
        if str(i[5]) == str(doctoapprove):
            c.execute(f"UPDATE doctors SET status=1 WHERE doc_id={str(doctoapprove)}")
            conn.commit()
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminlogin.html', mess=f'Врач успешно одобрен',
                                   patient_reg_requests=patient_reg_requests, doctor_reg_requests=doctor_reg_requests,
                                   registered_patients=registered_patients, registered_doctors=registered_doctors,
                                   l1=l1, l2=l2, l3=l3, l4=l4)
    else:
        patient_reg_requests = ret_patient_reg_requests()
        doctor_reg_requests = ret_doctor_reg_requests()
        registered_patients = ret_registered_patients()
        registered_doctors = ret_registered_doctors()
        l1 = len(patient_reg_requests)
        l2 = len(doctor_reg_requests)
        l3 = len(registered_patients)
        l4 = len(registered_doctors)
        return render_template('adminlogin.html', mess=f'Ошибка одобрения врача',
                               patient_reg_requests=patient_reg_requests, doctor_reg_requests=doctor_reg_requests,
                               registered_patients=registered_patients, registered_doctors=registered_doctors, l1=l1,
                               l2=l2, l3=l3, l4=l4)


# Одобрение пациента администратором
@app.route('/approvepatient')
def approvepatient():
    pattoapprove = request.values['patnum']
    c.execute('SELECT * FROM patients')
    conn.commit()
    patient_requests = c.fetchall()
    for i in patient_requests:
        if str(i[3]) == str(pattoapprove):
            c.execute(f"UPDATE patients SET status=1 WHERE phone_number={str(pattoapprove)}")
            conn.commit()
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminlogin.html', mess=f'Пациент успешно одобрен',
                                   patient_reg_requests=patient_reg_requests, doctor_reg_requests=doctor_reg_requests,
                                   registered_patients=registered_patients, registered_doctors=registered_doctors,
                                   l1=l1, l2=l2, l3=l3, l4=l4)

    else:
        patient_reg_requests = ret_patient_reg_requests()
        doctor_reg_requests = ret_doctor_reg_requests()
        registered_patients = ret_registered_patients()
        registered_doctors = ret_registered_doctors()
        l1 = len(patient_reg_requests)
        l2 = len(doctor_reg_requests)
        l3 = len(registered_patients)
        l4 = len(registered_doctors)
        return render_template('adminlogin.html', mess=f'Ошибка одобрения пациента',
                               patient_reg_requests=patient_reg_requests, doctor_reg_requests=doctor_reg_requests,
                               registered_patients=registered_patients, registered_doctors=registered_doctors, l1=l1,
                               l2=l2, l3=l3, l4=l4)


# Одобрение записи врачом
@app.route('/doctorapproveappointment')
def doctorapproveappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    patname = request.values['patname']
    appdate = request.values['appdate']
    c.execute(f"INSERT INTO doctorappointments VALUES ('{docid}','{patname}','{patnum}','{appdate}')")
    conn.commit()
    c.execute(f"DELETE FROM doctorappointmentrequests WHERE patientnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_doctor, l1 = retapprequests(docid)
    fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
    return render_template('doctorlogin.html',
                           appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                           fix_appointment_for_this_doctor=fix_appointment_for_this_doctor, l1=l1, l2=l2, docid=docid)


# Удаление записи врачом
@app.route('/doctordeleteappointment')
def doctordeleteappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM doctorappointmentrequests WHERE patientnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_doctor, l1 = retapprequests(docid)
    fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
    return render_template('doctorlogin.html',
                           appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                           fix_appointment_for_this_doctor=fix_appointment_for_this_doctor, l1=l1, l2=l2, docid=docid)


# Удаление запроса врача
@app.route('/deletedoctorrequest')
def deletedoctorrequest():
    docid = request.values['docid']
    c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}'")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminlogin.html', patient_reg_requests=patient_reg_requests,
                           doctor_reg_requests=doctor_reg_requests, registered_patients=registered_patients,
                           registered_doctors=registered_doctors, l1=l1, l2=l2, l3=l3, l4=l4)


### Удаление запроса пациента
@app.route('/deletepatientrequest')
def deletepatientrequest():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}'")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminlogin.html', patient_reg_requests=patient_reg_requests,
                           doctor_reg_requests=doctor_reg_requests, registered_patients=registered_patients,
                           registered_doctors=registered_doctors, l1=l1, l2=l2, l3=l3, l4=l4)


# Обновление данных пациента
@app.route('/updatepatient')
def updatepatient():
    phn = request.args.get('phn')  # Безопасное получение параметра
    if not phn:
        return render_template('updatepatient.html', mess="Номер телефона не указан")

    patient = getpatdetails(phn)
    if not patient:
        return render_template('updatepatient.html', mess="Пациент не найден")

    # Правильная распаковка (убедитесь, что структура таблицы совпадает)
    fn, ln, dob, phn_db, passw, add, status = patient
    return render_template('updatepatient.html',
                           fn=fn, ln=ln, dob=dob, phn=phn_db,
                           add=add)


# Обновление данных врача
@app.route('/updatedoctor')
def updatedoctor():
    docid = request.args['docid']
    fn, ln, dob, phn, add, docid, passw, spec, status = getdocdetails(docid)
    return render_template('updatedoctor.html', fn=fn, ln=ln, dob=dob, phn=phn, passw=passw, add=add, status=status,
                           spec=spec, docid=docid)


# Сохранение изменений врача
@app.route('/makedoctorupdates', methods=['GET', 'POST'])
def makedoctorupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.args['docid']
    spec = request.form['speciality']
    c.execute("UPDATE doctors SET first_name=(?) WHERE doc_id=(?)", (firstname, docid))
    conn.commit()
    c.execute("UPDATE doctors SET last_name=(?) WHERE doc_id=(?)", (lastname, docid))
    conn.commit()
    c.execute("UPDATE doctors SET dob=(?) WHERE doc_id=(?)", (dob, docid))
    conn.commit()
    c.execute("UPDATE doctors SET phone_number=(?) WHERE doc_id=(?)", (phn, docid))
    conn.commit()
    c.execute("UPDATE doctors SET address=(?) WHERE doc_id=(?)", (address, docid))
    conn.commit()
    c.execute("UPDATE doctors SET speciality=(?) WHERE doc_id=(?)", (spec, docid))
    conn.commit()
    return render_template('doctorlogin.html', mess='Данные успешно обновлены')


# Сохранение изменений пациента
@app.route('/makepatientupdates', methods=['GET', 'POST'])
def makepatientupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.args['phn']
    address = request.form['address']
    c.execute("UPDATE patients SET first_name=(?) WHERE phone_number=(?)", (firstname, phn))
    conn.commit()
    c.execute("UPDATE patients SET last_name=(?) WHERE phone_number=(?)", (lastname, phn))
    conn.commit()
    c.execute("UPDATE patients SET dob=(?) WHERE phone_number=(?)", (dob, phn))
    conn.commit()
    c.execute("UPDATE patients SET address=(?) WHERE phone_number=(?)", (address, phn))
    conn.commit()
    return render_template('patientlogin.html', mess='Данные успешно обновлены')


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
