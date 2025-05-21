#! /usr/bin/python3.11
from data.routes import app

if __name__ == '__main__':
    app.run(port=5003, host='yl.ielista.ru')