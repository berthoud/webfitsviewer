#from search import app as application
#from app import app
from wsgiref.handlers import CGIHandler
#from db_config import mysql
from werkzeug.security import generate_password_hash, check_password_hash



#import os, sys
#currentdir = os.path.dirname(os.path.realpath(__file__))
#parentdir = os.path.dirname(currentdir)
#sys.path.append(parentdir)
from search_app.custom.tables import ResultsFile, Results_Cq1, Results_Cq2, Results_Cq3, Results_Cq4, Results_Cq5, Results_Sq2
from search_app.custom.forms import S_SearchForm, Moon_SearchForm
from flaskext.mysql import MySQL
from flask import Flask, flash, render_template, request, redirect
import pymysql
import mysql.connector
import os


#readConfigs = os.path.join( os.getcwd(), '../../database/', 'create_database.py' )
#from readConfigs import default_sql_user, default_sql_pass, sql_user, sql_pass
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


@app.route('/out')
def disconn():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            print(e)
        finally:
            #print("disconn:", conn)
            cursor.close()
            conn.close()
        flash('Your connection closed')
        return render_template('_initdb.html')


# =====================================================================
#         LANDING PAGE : CREATE/USE stars_db
# =====================================================================
@app.route('/')
def init():
        global conn
        global cursor
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        #print("LOAD init")
        return render_template('_initdb.html')

@app.route('/restart')
def restart():
        #print("*** deleted database ***")
        DROP_DB = """DROP DATABASE seo"""
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(DROP_DB)

        return redirect('/out')

@app.route('/populate')
def populate():
        flash('Success in populate database!')
        return redirect('/start')

# [end] --------------------
# [end - show tables] --------------------


# =====================================================================
#         START : HOME, INITIALIZE
# =====================================================================
@app.route('/start')
def start():
        global CREATE_DB
        global USE_DB
        global conn
        global cursor
        #print("start = ", USE_DB)
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        CREATE_DB = """CREATE DATABASE IF NOT EXISTS seo """
        USE_DB = """USE seo"""

        cursor.execute(CREATE_DB)
        cursor.execute(USE_DB)
        return redirect('/search')


# [end] --------------------
# index
@app.route('/search', methods=['GET', 'POST'])
def search_view():
    #print("in SEARCH_VIEW")
    search = S_SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)

@app.route('/results')
def search_results(search):
    results = []
    select_string = search.data['select_file']

    file_string = search.data['search_file']
    date_string = search.data['search_date']
    ra_string = search.data['search_ra']
    dec_string = search.data['search_dec']
    exptime_string = search.data['search_exptime']


    sql_table = select_string
    file_col = ''
    date_col = ''
    ra_col = ''
    dec_col = ''
    exptime_col = ''
    count = 0


    if (search.data['search_file'] == '' and search.data['search_date'] == ''  and search.data['search_ra'] == '' and search.data['search_dec'] == '' and search.data['search_exptime'] == '') :
        flash('Empty search. Please try again!')
        return redirect('/search')

    query = "SELECT * FROM fits_data WHERE"

    if search.data['search_file'] != '' :
        file_col = 'file_path'
        query += " file_path LIKE '%"+file_string+"%'"
        count += 1

    if search.data['search_date'] != '' :
        date_col = 'date_obs'
        if count == 0:
            query += " CAST(date_obs AS CHAR) LIKE '%"+date_string+"%'"
        else:
            query += " AND CAST(date_obs AS CHAR) LIKE '%"+date_string+"%'"
        count += 1

    if search.data['search_ra'] != '' :
        ra_col = 'ra'
        if count == 0:
            query += " CAST(ra AS CHAR) LIKE '%"+ra_string+"%'"
        else:
            query += " AND CAST(ra AS CHAR) LIKE '%"+ra_string+"%'"
        count += 1

    if search.data['search_dec'] != '' :
        dec_col = 'dec'
        count += 1

    if search.data['search_exptime'] != '' :
        exptime_col = 'exptime'
        count += 1

    # fields for all cols, include if not empty
    cursor.execute(query)
    results = cursor.fetchall()
    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results

        #print("table = RESULTS FILE")
        table = ResultsFile(results)
        table.border = True
        return render_template('results.html', table=table)


# =====================================================================
#         SHOW TABLES
# =====================================================================
@app.route('/all_files')
def show_files():
        try:
            cursor.execute("SELECT * FROM fits_data")
            rows = cursor.fetchall()
            table = ResultsFile(rows)
            table.border = True
            return render_template('allfiles.html', table=table)
        except Exception as e:
            print(e)
# [end] --------------------


# ====================================================================
# ADDING NEW ATTRIBUTES
# =====================================================================

@app.route('/new_file')
def add_file_view():
        try:
            return render_template('addFile.html')
        except Exception as e:
            print(e)

@app.route('/addFile', methods=['POST'])
def add_file():
        #print(" add_file ")
        try:
            _fid = request.form['inputFileId']
            _oname = request.form['inputObjectName']
            _gid = request.form['inputGroupId']
            _reds = request.form['inputReductionStage']
            _fileType = request.form['inputFileType']
            _bandType = request.form['inputBandType']
            _quality = request.form['inputQuality']
            _position = request.form['inputPosition']
            _date = request.form['inputDate']
            _time = request.form['inputTime']
            _timeStamp = 'timeNow'
            # validate the received values
            if (_fid and _oname and _date and request.method == 'POST'):
                #do not save password as a plain text
		# save edits
                sql = "INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (_fid, _oname, _gid, _reds, _fileType, _bandType, _quality, _position, _date, _time, _timeStamp)
                #print(sql,data)
                cursor.execute(DISABLE_FK)
                cursor.execute(sql, data)
                cursor.execute(ENABLE_FK)
                conn.commit()
                flash('File added successfully!')
                return redirect('/all_files')
            else:
                return 'Error while adding File'
        except Exception as e:
            print(e)

@app.route('/editF/<string:id>')
def edit_file_view(id):
	try:
            #print("editF fileid = %s", id)
            cursor.execute("SELECT * FROM files WHERE fileId=%s", id)
            row = cursor.fetchone()
            if row:
                return render_template('editFile.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)

@app.route('/update', methods=['POST'])
def update_user():
	try:
                _uid = request.form['id']
                _fname = request.form['inputFName']
                _lname = request.form['inputLName']
                _email = request.form['inputEmail']
                _password = request.form['inputPassword']
                _permissions = request.form['inputPermissions']
                # validate the received values
                if (_lname and _email and _uid and request.method == 'POST'):
                    #do not save password as a plain text
                    _hashed_password = generate_password_hash(_password)
                    #print(_hashed_password)
                    # save edits
                    sql = "UPDATE users SET userId=%s, password=%s, firstName=%s, lastName=%s, email=%s, permissions=%s WHERE userId=%s"
                    data = (_uid, _hashed_password, _fname, _lname, _email, _permissions, _uid,)
                    cursor.execute(sql, data)
                    conn.commit()
                    flash('User updated successfully!')
                    return redirect('/all_users')
                else:
                    return 'Error while updating user. Email. last name, and user id are required fields.'
	except Exception as e:
            print(e)


@app.route('/updateF', methods=['POST'])
def update_file():
	try:
                _fid = request.form['inputFileId']
                _oname = request.form['inputObjectName']
                _gid = request.form['inputGroupId']
                _reds = request.form['inputReductionStage']
                _fileType = request.form['inputFileType']
                _bandType = request.form['inputBandType']
                _quality = request.form['inputQuality']
                _position = request.form['inputPosition']
                _date = request.form['inputDate']
                _time = request.form['inputTime']
                _timeStamp = 'timeNow'
                # validate the received values
                if (_fid and _oname and _timeStamp and request.method == 'POST'):
                    # save edits
                    sql = "UPDATE files SET fileId=%s, objectName=%s, groupId=%s, reductionStage=%s, fileType=%s, bandType=%s, quality=%s, position=%s, date=%s, time=%s, timeStamp =%s WHERE fileId=%s"
                    data = (_fid, _oname, _gid, _reds, _fileType, _bandType, _quality, _position, _date, _time, _timeStamp, _fid)
                    cursor.execute(sql, data)
                    conn.commit()
                    flash('File updated successfully!')
                    return redirect('/all_files')
                else:
                    return 'Error while updating file'
	except Exception as e:
            print(e)


@app.route('/deleteF/<string:id>')
def delete_file(id):
	try:
		cursor.execute("DELETE FROM files WHERE fileId=%s", (id,))
		conn.commit()
		flash('File deleted successfully!', 'success')
		return redirect('/all_files')
	except Exception as e:
		print(e)

# =====================================================================
#         SIMPLE QUERIES :
# =====================================================================
# 1: Search tables by primary key containing value
# 2: Show observations in order of Oldest to Latest
# 3: Show Day and moonphase
            #cursor.execute("SELECT * FROM observations ORDER BY startDate ASC")

# [end] --------------------

# =====================================================================
#         COMPLEX QUERIES :
# =====================================================================
#

@app.route('/cq_1')
def show_cq_1():
        try:
            cursor.execute("SELECT F.fileId, F.groupId, F.date,  O.startDate, O.endDate FROM observations as O RIGHT JOIN files as F on F.groupId = O.groupId")
            rows = cursor.fetchall()
            table = Results_Cq1(rows)
            table.border = True
            flash('Join files and observation tables')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)

@app.route('/cq_2')
def show_cq_2():
        try:
            cursor.execute("SELECT F.groupId, F.fileId, F.objectName, W.dayId, W.moonPhase FROM files as F, weatherDaily as W WHERE F.date = W.dayId AND W.moonPhase = 'Full'")
            rows = cursor.fetchall()
            table = Results_Cq2(rows)
            table.border = True
            flash('List files in observation group where date falls on a full moon')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)



@app.route('/cq_3')
def show_cq_3():
        try:
            cursor.execute("Select * from observations where groupId = ANY (SELECT p.groupId from (SELECT x.groupId, COUNT(*) as mc from (Select groupId, count(objectName) from files group by objectName, groupId) as x GROUP BY x.groupId) as p WHERE p.mc = (Select Max(b.total) as mc from (Select a.groupId, count(a.objectName) as total from files as a group by a.objectName, a.groupId) as b))")

            rows = cursor.fetchall()
            table = Results_Cq3(rows)
            table.border = True
            flash('List observations containing at least one file for every astronomical object listed')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)



@app.route('/cq_4')
def show_cq_4():
        try:
            cursor.execute("SELECT * from files as F WHERE F.groupId = ANY (SELECT O.groupID from observations as O WHERE Not O.startDate = ANY (SELECT W.dayId from weatherDaily as W))")
            rows = cursor.fetchall()
            table = Results_Cq4(rows)
            table.border = True
            flash('List file names for observations that start on a date no weather data')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)


@app.route('/cq_5')
def show_cq_5():
        try:
            cursor.execute("SELECT Y.objectName, Y.Total_Files as filesTotal, Y.Total_Bands as bandsTotal, N.Dates as totalDays FROM (SELECT b.objectName, SUM(Filters) as Total_Files, COUNT(b.bandType) as Total_Bands FROM (SELECT x.bandType, x.objectName, COUNT(x.bandType) as Filters FROM files as x GROUP BY x.bandType, x.objectName ORDER BY x.objectName) as b GROUP BY b.objectName) as Y JOIN (SELECT x.objectName, COUNT(x.date) as Dates FROM (SELECT objectName, date from files GROUP BY objectName, date) as x GROUP BY x.objectName) as N ON N.objectName = Y.objectName;")
            rows = cursor.fetchall()
            table = Results_Cq5(rows)
            table.border = True
            flash('List total files, band types, and days per astronomical object')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)






#if __name__ == "__main__":
#    app.run()
    #CGIHandler().run(app)
