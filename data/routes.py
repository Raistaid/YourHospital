from flask import Flask, request, render_template
from config import logger
from database import conn, c
from utils import *
from models import *

app = Flask(__name__)

# Главная страница
@app.route('/')
def home():
    logger.info("Открыта главная страница")
    return render_template('home.html')


# Отображает страницу регистрации пациента
@app.route('/patreg')
def patreg():
    logger.info("Открыта страница регистрации пациента")
    return render_template('patientregistration.html')


# Отображает страницу регистрации врача
@app.route('/docreg')
def docreg():
    logger.info("Открыта страница регистрации врача")
    return render_template('doctorregistration.html')


# Отображает страницу входа для пациента
@app.route('/loginpage1')
def loginpage1():
    logger.info("Открыта страница входа для пациента")
    return render_template('loginpage1.html')


# Отображает страницу входа для врача
@app.route('/loginpage2')
def loginpage2():
    logger.info("Открыта страница входа для врача")
    return render_template('loginpage2.html')


# Отображает страницу входа для администратора
@app.route('/loginpage3')
def loginpage3():
    logger.info("Открыта страница входа для администратора")
    return render_template('loginpage3.html')


# Регистрация пациентов
@app.route('/addpatient', methods=['POST'])
def addpatient():
    logger.info("Обработка формы регистрации пациента")
    try:
        passw = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dob = request.form['dob']
        phn = request.form['phn']
        address = request.form['address']

        logger.debug(f"Получены данные: {firstname} {lastname}, {dob}, {phn}, {address}")

        if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
            logger.warning("Ошибка валидации имени и фамилии")
            return render_template('home.html', mess='Имя и фамилия должны содержать только буквы')

        if not checkpass(passw):
            logger.warning("Ошибка валидации пароля")
            return render_template('home.html', mess="Пароль должен быть длиной более 8 символов и содержать буквы, цифры и спецсимволы ('@','$','!')")

        if str(phn) in get_all_patnums():
            logger.warning(f"Попытка повторной регистрации пациента с номером: {phn}")
            return render_template('home.html', mess=f'Пациент с номером {phn} уже существует')

        c.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, 0)", (firstname, lastname, dob, phn, passw, address))
        conn.commit()
        logger.info(f"Запрос на регистрацию пациента {firstname} успешно добавлен")
        return render_template('home.html', mess=f'Запрос на регистрацию пациента {firstname} отправлен администратору')

    except Exception as e:
        logger.exception("Ошибка при регистрации пациента")
        return render_template('home.html', mess='Ошибка сервера')

# Регистрация врачей
@app.route('/adddoctor', methods=['GET', 'POST'])
def adddoctor():
    logger.info("Обработка формы регистрации врача")
    try:
        passw = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dob = request.form['dob']
        phn = request.form['phn']
        address = request.form['address']
        docid = request.form['docid']
        spec = request.form['speciality']

        logger.debug(f"Получены данные врача: {firstname} {lastname}, {dob}, {phn}, {address}, {docid}, {spec}")

        if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
            logger.warning("Ошибка валидации имени и фамилии врача")
            return render_template('home.html', mess='Имя и фамилия должны содержать только буквы')

        if not checkonlyalpha(spec):
            logger.warning("Ошибка валидации специальности врача")
            return render_template('home.html', mess='Специальность врача должна содержать только буквы')

        if not checkpass(passw):
            logger.warning("Ошибка валидации пароля врача")
            return render_template('home.html', mess="Пароль должен быть длиной более 8 символов и содержать буквы, цифры и спецсимволы ('@','$','!')")

        if str(docid) in get_all_docids():
            logger.warning(f"Попытка регистрации врача с существующим ID: {docid}")
            return render_template('home.html', mess=f'Врач с ID {docid} уже существует.')

        if str(phn) in get_all_patnums():
            logger.warning(f"Номер телефона {phn} уже зарегистрирован")
            return render_template('home.html', mess=f'Номер {phn} уже зарегистрирован.')

        c.execute(f"INSERT INTO doctors VALUES ('{firstname}','{lastname}','{dob}','{phn}','{address}','{docid}','{passw}','{spec}',0)")
        conn.commit()
        logger.info(f"Запрос на регистрацию врача {firstname} успешно добавлен")
        return render_template('home.html', mess=f'Запрос на регистрацию врача {firstname} отправлен администратору.')

    except Exception as e:
        logger.exception("Ошибка при регистрации врача")
        return render_template('home.html', mess='Ошибка сервера')

# Вход для пациентов
@app.route('/patientlogin', methods=['POST'])
def patientlogin():
    logger.info("Попытка входа пациента")
    phn = request.form.get('phn')
    passw = request.form.get('pass')

    if not phn or not passw:
        logger.warning("Не указан телефон или пароль")
        return render_template('loginpage1.html', err='Укажите телефон и пароль')

    c.execute('SELECT * FROM patients WHERE phone_number=? AND password=?', (phn, passw))
    patient = c.fetchone()

    if not patient:
        logger.warning("Неверный телефон или пароль пациента")
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

        logger.info(f"Пациент {patname} успешно вошел")

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
        logger.exception("Ошибка при входе пациента")
        return render_template('patientlogin.html', mess="Ошибка загрузки данных", phn=phn)

# Вход для врачей
@app.route('/doctorlogin', methods=['GET', 'POST'])
def doctorlogin():
    logger.info("Попытка входа врача")
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
                logger.info(f"Врач {i[0]} успешно вошел")
                appointment_requests_for_this_doctor, l1 = retapprequests(docid)
                fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
                return render_template('doctorlogin.html',
                                       appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                                       fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                                       l1=l1, l2=l2,
                                       docname=i[0],
                                       docid=docid)
        logger.warning("Неверные учетные данные врача")
        return render_template('loginpage2.html', err='Неверные учетные данные')

    # Если это GET-запрос (возврат с других страниц)
    elif request.method == 'GET' and docid:
        for i in registerd_doctors:
            if str(i[5]) == str(docid):
                logger.info(f"Врач {i[0]} вошел через GET-запрос")
                appointment_requests_for_this_doctor, l1 = retapprequests(docid)
                fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
                return render_template('doctorlogin.html',
                                       appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                                       fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,
                                       l1=l1, l2=l2,
                                       docname=i[0],
                                       docid=docid)
        logger.warning("Сессия врача устарела")
        return render_template('loginpage2.html', err='Сессия устарела')
    else:
        logger.warning("Попытка входа врача без авторизации")
        return render_template('loginpage2.html', err='Требуется авторизация')


# Вход для администратора
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    logger.info("Попытка входа администратора")
    try:
        username = request.form['username']
        passw = request.form['pass']
        c.execute('SELECT * FROM superusercreds')
        conn.commit()
        superusercreds = c.fetchall()

        for i in superusercreds:
            if str(i[0]) == str(username) and str(i[1]) == str(passw):
                logger.info("Администратор успешно вошел")
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
        logger.warning("Неверный логин или пароль администратора")
        return render_template('loginpage3.html', err='Неверный логин или пароль.')

    except Exception as e:
        logger.exception("Ошибка при входе администратора")
        return render_template('loginpage3.html', err='Ошибка сервера')


# Удаление пациентов
@app.route('/deletepatient', methods=['GET', 'POST'])
def deletepatient():
    patnum = request.values['patnum']
    logger.info(f"Удаление пациента с номером телефона: {patnum}")
    try:
        c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}'")
        conn.commit()
        logger.debug("Пациент удалён успешно")
    except Exception as e:
        logger.exception("Ошибка при удалении пациента")

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

# Удаление врача
@app.route('/deletedoctor', methods=['GET', 'POST'])
def deletedoctor():
    docid = request.values['docid']
    logger.info(f"Удаление врача с ID: {docid}")
    try:
        c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}'")
        conn.commit()
        logger.debug("Врач удалён успешно")
    except Exception as e:
        logger.exception("Ошибка при удалении врача")

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

        logger.info(f"Создание записи: пациент={phn}, врач={whichdoctor}, дата={appdate}")

        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()
        docnames = [getdocname(app[0]) for app in docsandapps]

        # Проверка заполненности полей
        if not all([phn, appdate, whichdoctor]):
            logger.warning("Поля не заполнены")
            return render_template('patientlogin.html', mess="Заполните все поля: врач и дата", phn=phn,
                                   docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)

        patname = getpatname(phn)
        if patname == -1:
            logger.warning("Пациент не найден")
            return render_template('patientlogin.html', mess="Пациент не найден", phn=phn,
                                   docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)

        appdate_obj = datetime.strptime(appdate, '%Y-%m-%d').date()
        if appdate_obj <= datetime.now().date():
            logger.warning("Выбрана дата не в будущем")
            return render_template('patientlogin.html', mess="Выберите дату в будущем", phn=phn,
                                   docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)

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
            logger.warning("Врач не найден")
            return render_template('patientlogin.html', mess="Врач не найден", phn=phn,
                                   docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)

        c.execute('''
            INSERT INTO doctorappointmentrequests (docid, patientname, patientnum, appointmentdate)
            VALUES (?, ?, ?, ?)
        ''', (docid, patname, phn, appdate))
        conn.commit()
        logger.info("Запрос на приём успешно создан")

        return render_template('patientlogin.html', mess="Запрос отправлен врачу", phn=phn,
                               docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)
    except Exception as e:
        logger.exception("Ошибка при создании записи")
        docsandapps, l = retalldocsandapps()
        docname_docid, l2 = ret_docname_docspec()
        docnames = [getdocname(app[0]) for app in docsandapps]
        return render_template('patientlogin.html', mess="Ошибка сервера. Попробуйте позже", phn=phn,
                               docname_docid=docname_docid, docsandapps=docsandapps, l=l, l2=l2, docnames=docnames)

# Одобрение врача администратором
@app.route('/approvedoctor')
def approvedoctor():
    doctoapprove = request.values['docid']
    c.execute('SELECT * FROM doctors')
    logger.info(f"Одобрение врача: ID={doctoapprove}")
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
            logger.info("Врач успешно одобрен")
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
        logger.info("Врач успешно одобрен")
        return render_template('adminlogin.html', mess=f'Ошибка одобрения врача',
                               patient_reg_requests=patient_reg_requests, doctor_reg_requests=doctor_reg_requests,
                               registered_patients=registered_patients, registered_doctors=registered_doctors, l1=l1,
                               l2=l2, l3=l3, l4=l4)


# Одобрение пациента администратором
@app.route('/approvepatient')
def approvepatient():
    pattoapprove = request.values['patnum']
    logger.info(f"Одобрение пациента: номер={pattoapprove}")
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
            logger.info("Пациент успешно одобрен")
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
        logger.exception("Ошибка при одобрении пациента")
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
    logger.info(f"Врач {docid} одобряет запись пациента {patname} ({patnum}) на дату {appdate}")

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
    logger.debug("Запись одобрена и запрос удалён")
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
    logger.info(f"Удаление записи: врач={docid}, пациент={patnum}")
    try:
        c.execute(f"DELETE FROM doctorappointmentrequests WHERE patientnum='{str(patnum)}'")
        conn.commit()
        logger.debug("Запись удалена успешно")
    except Exception as e:
        logger.exception("Ошибка при удалении записи")

    appointment_requests_for_this_doctor, l1 = retapprequests(docid)
    fix_appointment_for_this_doctor, l2 = retdocsandapps(docid)
    return render_template('doctorlogin.html',
                           appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,
                           fix_appointment_for_this_doctor=fix_appointment_for_this_doctor, l1=l1, l2=l2, docid=docid)


# Удаление запроса врача
@app.route('/deletedoctorrequest')
def deletedoctorrequest():
    docid = request.values['docid']
    logger.info(f"Удаление запроса врача: ID={docid}")
    try:
        c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}'")
        conn.commit()
        logger.debug("Запрос врача удалён")
    except Exception as e:
        logger.exception("Ошибка при удалении запроса врача")

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
    logger.info(f"Удаление запроса пациента: номер={patnum}")
    try:
        c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}'")
        conn.commit()
        logger.debug("Запрос пациента удалён")
    except Exception as e:
        logger.exception("Ошибка при удалении запроса пациента")

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
    logger.info(f"Обновление данных пациента: номер={phn}")
    if not phn:
        logger.warning("Не указан номер телефона пациента")
        return render_template('updatepatient.html', mess="Номер телефона не указан")

    patient = getpatdetails(phn)
    if not patient:
        logger.warning("Пациент не найден")
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
    logger.info(f"Обновление данных врача: ID={docid}")
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
    logger.info(f"Сохранение обновлений для врача: ID={docid}")
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
        logger.debug("Обновления врача сохранены")
        return render_template('doctorlogin.html',
                            mess='Данные успешно обновлены',
                            docid=docid,
                            docname=doc_details[0],
                            appointment_requests_for_this_doctor=appointment_requests,
                            fix_appointment_for_this_doctor=confirmed_appointments,
                            l1=len(appointment_requests),
                            l2=len(confirmed_appointments))

    except Exception as e:
        logger.exception("Ошибка при сохранении данных врача")
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
    logger.info("Сохранение обновлений для пациента")
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
        logger.debug("Обновления пациента сохранены")
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
        logger.exception("Ошибка при обновлении данных пациента")
        return render_template('updatepatient.html',
                               mess="Ошибка обновления данных",
                               phn=phn,
                               fn=firstname,
                               ln=lastname,
                               dob=dob,
                               add=address)