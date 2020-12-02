from flask import Flask, flash, render_template, request, redirect
from flaskext.mysql import MySQL
from my_app.custom.tables import * #ResultsFile, Results_Cq1, Results_Cq2, Results_Cq3, Results_Cq4, Results_Cq5, Results_Sq2
#from custom.forms import S_SearchForm, Moon_SearchForm

import pymysql
import mysql.connector

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'astrodatabase'
app.config['MYSQL_DATABASE_DB'] = 'seo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

CREATE_DB = ""
USE_DB = ""
DISABLE_FK = "SET foreign_key_checks = 0"
ENABLE_FK = "SET foreign_key_checks = 1"
conn = None
cursor = None

@app.route('/')
def hello_world():
    return 'Hello, add flask, py+mysql & connector, configs, custom, tables -my_app'
