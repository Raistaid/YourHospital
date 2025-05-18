from datetime import datetime
import sqlite3
from flask import Flask, request, render_template

# Определение Flask приложения
app = Flask(__name__)

# Код для SQLite 3

conn = sqlite3.connect('database/lifecare.db', check_same_thread=False)
c = conn.cursor()

# Создание таблиц
# Создание таблицы doctors, если она не существует
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

# Создание таблицы patients, если она не существует
c.execute('''CREATE TABLE IF NOT EXISTS patients(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            password integer text,
            address text,
            status integer
            )''')

# Создание таблицы superusercreds для хранения учетных данных администратора
c.execute('''CREATE TABLE IF NOT EXISTS superusercreds(
            username integer text,
            password integer text
            )''')

# Создание таблицы для хранения запросов на прием к врачу
c.execute('''CREATE TABLE IF NOT EXISTS doctorappointmentrequests(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
            )''')

# Создание таблицы для подтвержденных записей к врачу
c.execute('''CREATE TABLE IF NOT EXISTS doctorappointments(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
            )''')

# Инициализация админа, если учетные данные отсутствуют
c.execute('SELECT * from superusercreds')
conn.commit()
adminuser = c.fetchall()
if not adminuser:
    c.execute("INSERT INTO superusercreds VALUES ('admin','admin')")
    conn.commit()


# Вспомогательные функции
def datetoday():
    """Возвращает текущую дату в формате 'ГГГГ-ММ-ДД'."""
    today = datetime.now().strftime("%Y-%m-%d")
    return today


def checkonlyalpha(x):
    """Проверяет, состоит ли строка только из букв."""
    return x.isalpha()


def checkonlynum(x):
    """Проверяет, состоит ли строка только из цифр."""
    return x.isdigit()


def checkpass(x):
    """Проверяет сложность пароля (минимум 8 символов, буквы, цифры и спецсимволы)."""
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


# Функции для работы с данными
def retalldocsandapps():
    """Возвращает все подтвержденные записи ко всем врачам и их количество."""
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    l = len(docsandapps)
    return docsandapps, l


def getpatdetails(phn):
    """Возвращает данные пациента по номеру телефона."""
    c.execute("SELECT * FROM patients WHERE phone_number=?", (phn,))
    conn.commit()
    patient = c.fetchone()
    return patient


def getdocdetails(docid):
    """Возвращает данные врача по его ID."""
    c.execute(f"SELECT * FROM doctors")
    conn.commit()
    doctors = c.fetchall()
    for i in doctors:
        if str(i[5]) == str(docid):
            return i


def retdocsandapps(docid):
    """Возвращает подтвержденные записи с актуальными именами пациентов."""
    c.execute('''
        SELECT 
            da.docid, 
            p.first_name || ' ' || p.last_name AS patient_name,
            da.patientnum, 
            da.appointmentdate 
        FROM doctorappointments da
        INNER JOIN patients p ON da.patientnum = p.phone_number
        WHERE da.docid = ?
    ''', (docid,))
    conn.commit()
    docsandapps2 = c.fetchall()
    return docsandapps2, len(docsandapps2)


def retapprequests(docid):
    """Возвращает запросы на прием для конкретного врача и их количество."""
    c.execute("SELECT * FROM doctorappointmentrequests")
    conn.commit()
    appreq = c.fetchall()
    appreq2 = []
    for i in appreq:
        if str(i[0]) == str(docid):
            appreq2.append(i)
    l = len(appreq2)
    return appreq2, l




def ret_patient_reg_requests():
    """Возвращает список запросов на регистрацию пациентов (статус 0)."""
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    patient_reg_requests = []
    for d in data:
        if str(d[-1]) == '0':
            patient_reg_requests.append(d)
    return patient_reg_requests


def ret_doctor_reg_requests():
    """Возвращает список запросов на регистрацию врачей (статус 0)."""
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    doctor_reg_requests = []
    for d in data:
        if str(d[-1]) == '0':
            doctor_reg_requests.append(d)
    return doctor_reg_requests


def ret_registered_patients():
    """Возвращает список одобренных пациентов (статус 1)."""
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    registered_patients = []
    for d in data:
        if str(d[-1]) == '1':
            registered_patients.append(d)
    return registered_patients


def ret_registered_doctors():
    """Возвращает список одобренных врачей (статус 1)."""
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    registered_doctors = []
    for d in data:
        if str(d[-1]) == '1':
            registered_doctors.append(d)
    return registered_doctors


def ret_docname_docspec():
    """Возвращает список врачей в формате 'Имя Фамилия | ID | Специальность'."""
    c.execute('SELECT first_name, last_name, doc_id, speciality FROM doctors WHERE status=1')
    conn.commit()
    registered_doctors = c.fetchall()
    docname_docid = []
    for doc in registered_doctors:
        formatted = f"{doc[0]} {doc[1]} | {doc[2]} | {doc[3]}"
        docname_docid.append(formatted)
    return docname_docid, len(docname_docid)


def getdocname(docid):
    """Возвращает имя и фамилию врача по его ID."""
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    for i in registered_doctors:
        if str(i[5]) == str(docid):
            return i[0] + '-' + i[1]


# Возвращает имя и фамилию пациента по номеру телефона
def getpatname(patnum):
    c.execute('SELECT * FROM patients')
    conn.commit()
    details = c.fetchall()
    for i in details:
        if str(i[3]) == str(patnum):
            return i[0] + ' ' + i[1]
    else:
        return -1


# Возвращает список всех ID врачей.
def get_all_docids():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docids = []
    for i in registered_doctors:
        docids.append(str(i[5]))
    return docids


# Возвращает список всех номеров телефонов пациентов
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


# Отображает страницу регистрации пациента
@app.route('/patreg')
def patreg():
    return render_template('patientregistration.html')


# Отображает страницу регистрации врача
@app.route('/docreg')
def docreg():
    return render_template('doctorregistration.html')


# Отображает страницу входа для пациента
@app.route('/loginpage1')
def loginpage1():
    return render_template('loginpage1.html')


# Отображает страницу входа для врача
@app.route('/loginpage2')
def loginpage2():
    return render_template('loginpage2.html')


# Отображает страницу входа для администратора
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

    if str(docid) in get_all_docids():
        return render_template('home.html', mess=f'Врач с ID {docid} уже существует.')
    if str(phn) in get_all_patnums():  # Проверка на уникальность номера
        return render_template('home.html', mess=f'Номер {phn} уже зарегистрирован.')
    c.execute(
        f"INSERT INTO doctors VALUES ('{firstname}','{lastname}','{dob}','{phn}','{address}','{docid}','{passw}','{spec}',0)")
    conn.commit()
    return render_template('home.html', mess=f'Запрос на регистрацию врача {firstname} отправлен администратору.')


# Вход для пациентов
@app.route('/patientlogin', methods=['POST'])
def patientlogin():
    phn = request.form.get('phn')
    passw = request.form.get('pass')

    if not phn or not passw:
        return render_template('loginpage1.html', err='Укажите телефон и пароль')

    c.execute('SELECT * FROM patients WHERE phone_number=? AND password=?', (phn, passw))
    patient = c.fetchone()

    if not patient:
        return render_template('loginpage1.html', err='Неверный телефон или пароль')

    try:
        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()

        print("DEBUG: docname_docid =", docname_docid)  # отладка

        docnames = []
        for app in docsandapps:
            doc_name = getdocname(app[0])
            docnames.append(doc_name)

        patname = f"{patient[0]} {patient[1]}"

        return render_template(
            'patientlogin.html',
            docsandapps=docsandapps,
            docnames=docnames,
            docname_docid=docname_docid,
            l=l,
            l2=l2,
            patname=patname,
            phn=phn,
            mess=f"Добро пожаловать, {patname}!"
        )

    except Exception as e:
        print("Ошибка patientlogin:", e)
        return render_template('patientlogin.html',
                               mess="Ошибка загрузки данных",
                               phn=phn)


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
@app.route('/makeappointment', methods=['POST'])
def makeappointment():
    try:
        phn = request.args.get('phn')
        appdate = request.form.get('appdate')
        whichdoctor = request.form.get('whichdoctor')

        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()
        docnames = [getdocname(app[0]) for app in docsandapps]

        # Проверка заполненности полей
        if not all([phn, appdate, whichdoctor]):
            return render_template('patientlogin.html',
                                   mess="Заполните все поля: врач и дата",
                                   phn=phn,
                                   docname_docid=docname_docid,
                                   docsandapps=docsandapps,
                                   l=l,
                                   l2=l2,
                                   docnames=docnames
                                   )

        patname = getpatname(phn)
        if patname == -1:
            return render_template('patientlogin.html',
                                   mess="Пациент не найден",
                                   phn=phn,
                                   docname_docid=docname_docid,
                                   docsandapps=docsandapps,
                                   l=l,
                                   l2=l2,
                                   docnames=docnames
                                   )

        docid = whichdoctor.strip()
        appdate_obj = datetime.strptime(appdate, '%Y-%m-%d').date()
        today = datetime.now().date()
        if appdate_obj <= today:
            return render_template('patientlogin.html',
                                   mess="Выберите дату в будущем",
                                   phn=phn,
                                   docname_docid=docname_docid,
                                   docsandapps=docsandapps,
                                   l=l,
                                   l2=l2,
                                   docnames=docnames
                                   )

        if docid not in get_all_docids():
            return render_template('patientlogin.html',
                                   mess="Врач не найден",
                                   phn=phn,
                                   docname_docid=docname_docid,
                                   docsandapps=docsandapps,
                                   l=l,
                                   l2=l2,
                                   docnames=docnames
                                   )

        c.execute('''
            INSERT INTO doctorappointmentrequests (docid, patientname, patientnum, appointmentdate)
            VALUES (?, ?, ?, ?)
        ''', (docid, patname, phn, appdate))
        conn.commit()

        return render_template('patientlogin.html',
                               mess="Запрос отправлен врачу",
                               phn=phn,
                               docname_docid=docname_docid,
                               docsandapps=docsandapps,
                               l=l,
                               l2=l2,
                               docnames=docnames
                               )

    except Exception as e:
        print(f"Ошибка makeappointment: {e}")
        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()
        docnames = [getdocname(app[0]) for app in docsandapps]

        return render_template('patientlogin.html',
                               mess="Ошибка сервера. Попробуйте позже",
                               phn=phn,
                               docname_docid=docname_docid,
                               docsandapps=docsandapps,
                               l=l,
                               l2=l2,
                               docnames=docnames
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
    docid = request.args.get('docid')
    patnum = request.args.get('patnum')
    patname = request.args.get('patname')
    appdate = request.args.get('appdate')

    # Добавить только если такой записи ещё нет
    c.execute('''SELECT * FROM doctorappointments 
                 WHERE docid=? AND patientnum=? AND appointmentdate=?''',
              (docid, patnum, appdate))
    if not c.fetchone():
        c.execute("INSERT INTO doctorappointments VALUES (?, ?, ?, ?)",
                  (docid, patname, patnum, appdate))
        conn.commit()

    # Удалить только одну строку (с конкретной датой и пациентом)
    c.execute('''DELETE FROM doctorappointmentrequests 
                 WHERE docid=? AND patientnum=? AND appointmentdate=?''',
              (docid, patnum, appdate))
    conn.commit()

    appointment_requests_for_this_doctor, l1 = retapprequests(docid)
    fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)

    return render_template('doctorlogin.html',
                           appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                           fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                           l1=l1, l2=l2,
                           docid=docid,
                           docname=getdocdetails(docid)[0])

@app.route('/doctordeleteconfirmedappointment')
def doctordeleteconfirmedappointment():
    docid = request.args.get('docid')
    patnum = request.args.get('patnum')
    appdate = request.args.get('appdate')

    c.execute('''
        DELETE FROM doctorappointments 
        WHERE docid=? AND patientnum=? AND appointmentdate=?
    ''', (docid, patnum, appdate))
    conn.commit()

    appointment_requests_for_this_doctor, l1 = retapprequests(docid)
    fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
    docname = getdocdetails(docid)[0]

    return render_template('doctorlogin.html',
                           appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                           fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                           l1=l1, l2=l2,
                           docid=docid,
                           docname=docname)

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


# Удаление запроса пациента
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
    phn = request.args.get('phn')
    if not phn:
        return render_template('updatepatient.html', mess="Номер телефона не указан")

    patient = getpatdetails(phn)
    if not patient:
        return render_template('updatepatient.html', mess="Пациент не найден")

    fn, ln, dob, phn_db, passw, add, status = patient
    return render_template('updatepatient.html',
                           fn=fn, ln=ln, dob=dob, phn=phn_db,
                           add=add)


# Обновление данных врача
@app.route('/updatedoctor')
def updatedoctor():
    docid = request.args['docid']
    doc_details = getdocdetails(docid)
    if not doc_details:
        return "Врач не найден", 404

    return render_template('updatedoctor.html',
                           fn=doc_details[0],
                           ln=doc_details[1],
                           dob=doc_details[2],
                           phn=doc_details[3],
                           add=doc_details[4],
                           spec=doc_details[7],
                           docid=docid)


# Сохранение изменений врача
@app.route('/makedoctorupdates', methods=['POST'])
def makedoctorupdates():
    docid = request.args.get('docid')
    if not docid:
        return "Ошибка: ID врача не указан", 400

    # Получаем новые данные из формы
    new_data = (
        request.form.get('firstname'),
        request.form.get('lastname'),
        request.form.get('dob'),
        request.form.get('phn'),
        request.form.get('address'),
        request.form.get('speciality'),
        docid  # Используем оригинальный docid для WHERE
    )

    try:
        # Обновляем данные одним запросом
        c.execute('''
            UPDATE doctors 
            SET first_name = ?,
                last_name = ?,
                dob = ?,
                phone_number = ?,
                address = ?,
                speciality = ?
            WHERE doc_id = ?
        ''', new_data)
        conn.commit()

        # Получаем обновленные данные для отображения
        appointment_requests, l1 = retapprequests(docid)
        confirmed_appointments, l2 = retdocsandapps(docid)
        doc_details = getdocdetails(docid)

        return render_template('doctorlogin.html',
                            mess='Данные успешно обновлены',
                            docid=docid,
                            docname=doc_details[0],
                            appointment_requests_for_this_doctor=appointment_requests,
                            fix_appointment_for_this_doctor=confirmed_appointments,
                            l1=len(appointment_requests),
                            l2=len(confirmed_appointments))

    except Exception as e:
        print(f"Ошибка обновления врача: {e}")
        conn.rollback()
        return render_template('updatedoctor.html',
                            mess="Ошибка обновления данных",
                            docid=docid)


# Сохранение изменений пациента
@app.route('/makepatientupdates', methods=['POST'])
def makepatientupdates():
    # Получаем PHN из URL-параметра
    phn = request.args.get('phn')

    # Получаем данные из формы
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    dob = request.form.get('dob')
    address = request.form.get('address')

    try:
        # Обновляем все поля одним запросом
        c.execute('''
            UPDATE patients 
            SET first_name = ?, 
                last_name = ?, 
                dob = ?, 
                address = ? 
            WHERE phone_number = ?
        ''', (firstname, lastname, dob, address, phn))
        conn.commit()

        # Получаем обновленные данные для отображения
        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()
        docnames = [getdocname(app[0]) for app in docsandapps]

        return render_template(
            'patientlogin.html',
            mess='Данные успешно обновлены',
            phn=phn,
            docsandapps=docsandapps,
            docnames=docnames,
            docname_docid=docname_docid,
            l=l,
            l2=l2
        )

    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        return render_template('updatepatient.html',
                               mess="Ошибка обновления данных",
                               phn=phn,
                               fn=firstname,
                               ln=lastname,
                               dob=dob,
                               add=address)
# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
