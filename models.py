from database import conn, c
from config import logger
from utils import datetoday
import sqlite3

def retalldocsandapps():
    logger.debug("Получение всех записей doctorappointments")
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    l = len(docsandapps)
    logger.debug(f"Найдено {l} записей")
    return docsandapps, l

def getpatdetails(phn):
    logger.debug(f"Получение данных пациента по номеру телефона: {phn}")
    c.execute("SELECT * FROM patients WHERE phone_number=?", (phn,))
    conn.commit()
    patient = c.fetchone()
    return patient

def getdocdetails(docid):
    logger.debug(f"Получение данных врача по ID: {docid}")
    c.execute(f"SELECT * FROM doctors")
    conn.commit()
    doctors = c.fetchall()
    for i in doctors:
        if str(i[5]) == str(docid):
            return i

def retdocsandapps(docid):
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
    logger.debug(f"Получение записей к врачу по ID: {docid}")
    conn.commit()
    docsandapps2 = c.fetchall()
    logger.debug(f"Найдено {len(docsandapps2)} записей для врача")
    return docsandapps2, len(docsandapps2)

def retapprequests(docid):
    c.execute("SELECT * FROM doctorappointmentrequests")
    logger.debug(f"Получение запросов на прием к врачу по ID: {docid}")
    conn.commit()
    appreq = c.fetchall()
    appreq2 = []
    for i in appreq:
        if str(i[0]) == str(docid):
            appreq2.append(i)
    l = len(appreq2)
    logger.debug(f"Найдено {len(appreq2)} запросов для врача")
    return appreq2, l

def ret_patient_reg_requests():
    logger.debug("Получение всех заявок на регистрацию пациентов")
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    patient_reg_requests = [d for d in data if str(d[-1]) == '0']
    logger.debug(f"Найдено {len(patient_reg_requests)} заявок")
    return patient_reg_requests

def ret_doctor_reg_requests():
    logger.debug("Получение всех заявок на регистрацию врачей")
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    doctor_reg_requests = []
    for d in data:
        if str(d[-1]) == '0':
            doctor_reg_requests.append(d)
    logger.debug(f"Найдено {len(doctor_reg_requests)} заявок")
    return doctor_reg_requests

def ret_registered_patients():
    logger.debug("Получение зарегистрированных пациентов")
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    registered_patients = []
    for d in data:
        if str(d[-1]) == '1':
            registered_patients.append(d)
    logger.debug(f"Найдено {len(registered_patients)} зарегистрированных пациентов")
    return registered_patients

def ret_registered_doctors():
    logger.debug("Получение зарегистрированных врачей")
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    registered_doctors = []
    for d in data:
        if str(d[-1]) == '1':
            registered_doctors.append(d)
    logger.debug(f"Найдено {len(registered_doctors)} зарегистрированных врачей")
    return registered_doctors

def ret_docname_docspec():
    logger.debug("Формирование списка врачей с ID и специальностью")
    c.execute('SELECT first_name, last_name, doc_id, speciality FROM doctors WHERE status=1')
    conn.commit()
    registered_doctors = c.fetchall()
    docname_docid = []
    for doc in registered_doctors:
        formatted = f"{doc[0]} {doc[1]} | {doc[2]} | {doc[3]}"
        docname_docid.append(formatted)
    logger.debug(f"Сформировано {len(docname_docid)} записей")
    return docname_docid, len(docname_docid)

def getdocname(docid):
    logger.debug(f"Получение имени врача по ID: {docid}")
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    for i in registered_doctors:
        if str(i[5]) == str(docid):
            return i[0] + '-' + i[1]

def getpatname(patnum):
    logger.debug(f"Получение имени пациента по номеру телефона: {patnum}")
    c.execute('SELECT * FROM patients')
    conn.commit()
    details = c.fetchall()
    for i in details:
        if str(i[3]) == str(patnum):
            return i[0] + ' ' + i[1]
    logger.debug("Пациент не найден")
    return -1

def get_all_docids():
    logger.debug("Получение всех ID врачей")
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docids = []
    for i in registered_doctors:
        docids.append(str(i[5]))
    logger.debug(f"Получено {len(docids)} ID")
    return docids

def get_all_patnums():
    logger.debug("Получение всех номеров пациентов")
    c.execute('SELECT * FROM patients')
    conn.commit()
    registered_patients = c.fetchall()
    patnums = []
    for i in registered_patients:
        patnums.append(str(i[3]))
    logger.debug(f"Получено {len(patnums)} номеров")
    return patnums