import sqlite3
from config import logger

# Подключение к SQLite 3
logger.debug("Инициализация подключения к SQLite...")
conn = sqlite3.connect('../database/lifecare.db', check_same_thread=False)
c = conn.cursor()

# Создание таблиц
def initialize_database():
    logger.info("Создание таблиц, если они не существуют")
    try:
        logger.debug("Создание таблицы doctors")
        c.execute('''CREATE TABLE IF NOT EXISTS doctors(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            address text,
            doc_id integer,
            password text,
            speciality text,
            status integer
        )''')

        logger.debug("Создание таблицы patients")
        c.execute('''CREATE TABLE IF NOT EXISTS patients(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            password integer text,
            address text,
            status integer
        )''')

        logger.debug("Создание таблицы superusercreds")
        c.execute('''CREATE TABLE IF NOT EXISTS superusercreds(
            username integer text,
            password integer text
        )''')

        logger.debug("Создание таблицы doctorappointmentrequests")
        c.execute('''CREATE TABLE IF NOT EXISTS doctorappointmentrequests(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
        )''')

        logger.debug("Создание таблицы doctorappointments")
        c.execute('''CREATE TABLE IF NOT EXISTS doctorappointments(
            docid integer text,
            patientname integer text,
            patientnum integer text,
            appointmentdate date
        )''')

        logger.debug("Проверка наличия учетных данных администратора")
        c.execute('SELECT * from superusercreds')
        conn.commit()
        adminuser = c.fetchall()
        if not adminuser:
            logger.info("Учетные данные администратора отсутствуют. Выполняется инициализация...")
            c.execute("INSERT INTO superusercreds VALUES ('admin','admin')")
            conn.commit()
            logger.info("Учетные данные администратора успешно добавлены")
        else:
            logger.info("Учетные данные администратора уже существуют")
    except Exception as e:
        logger.exception("Ошибка при создании таблиц или инициализации администратора")

initialize_database()
logger.debug("Инициализация базы данных завершена")