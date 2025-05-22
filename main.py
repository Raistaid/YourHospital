#! /usr/bin/python3.11
from routes import app
from database import initialize_database
import config

if __name__ == '__main__':
    app.run(port=5003, host='0.0.0.0', debug=True)