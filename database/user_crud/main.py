import pymysql
from app import app
from tables import Results, ResultsFile, ResultsObs, ResultsWD
from db_config import mysql
from flask import flash, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash


CREATE_DB = ""
USE_DB = ""
conn = None
cursor = None

def disconn():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            print(e)
        finally:
            print("disconn:", conn)
            cursor.close()
            conn.close()


# =====================================================================
#         LANDING PAGE : CREATE/USE stars_db
# =====================================================================
@app.route('/')
def init():
        global conn
        global cursor
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        print("LOAD init")
        return render_template('_initdb.html')

def ot():
        global CREATE_DB
        global USE_DB
        print("LOAD init", USE_DB)
        CREATE_DB = """CREATE DATABASE IF NOT EXISTS stars_db """
        USE_DB = """ USE stars_db """
        try:
            cursor.execute(CREATE_DB)
            cursor.execute(USE_DB)
            print("did Set db =", USE_DB)
        except Exception as e:
            print(e)
        finally:
            print("conn, cursor:", conn)

# [end] --------------------
# [end - show tables] --------------------


# =====================================================================
#         START : HOME, INITIALIZE
# =====================================================================
@app.route('/start')
def start():
        global CREATE_DB
        global USE_DB
        print("start = ", USE_DB)
        CREATE_DB = """CREATE DATABASE IF NOT EXISTS stars_db """
        USE_DB = """ USE stars_db """
        try:
            cursor.execute(CREATE_DB)
            cursor.execute(USE_DB)
            sqltb_u = """CREATE TABLE IF NOT EXISTS users (
                userId VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                firstName VARCHAR(50) DEFAULT NULL,
                lastName VARCHAR(50) DEFAULT NULL,
                email VARCHAR(100) DEFAULT NULL,
                permissions int(11) NOT NULL,
                PRIMARY KEY (userid))"""

            sqltb_ob = """CREATE TABLE IF NOT EXISTS observations (
                groupId VARCHAR(255) NOT NULL,
                fileId VARCHAR(255) NOT NULL,
                startTime DATETIME DEFAULT NULL,
                endTime DATETIME DEFAULT NULL,
                PRIMARY KEY (groupId, fileId))"""


            sqltb_f = """CREATE TABLE IF NOT EXISTS files (
                fileId VARCHAR(255) NOT NULL,
                objectName VARCHAR(50) DEFAULT NULL,
                groupId VARCHAR(255) DEFAULT NULL,
                reductionStage VARCHAR(50) DEFAULT NULL,
                fileType VARCHAR(50) DEFAULT NULL,
                bandType VARCHAR(20) DEFAULT NULL,
                quality VARCHAR(50) DEFAULT NULL,
                position NUMERIC(10,3) DEFAULT NULL,
                date DATE DEFAULT NULL,
                time TIME DEFAULT NULL,
                timeStamp VARCHAR(50) DEFAULT NULL,
                PRIMARY KEY (fileId))"""

            sqltb_wd = """CREATE TABLE IF NOT EXISTS weatherDaily (
                            dayId DATE NOT NULL,
                            sunriseTime TIME DEFAULT NULL,
                            sundownTime TIME DEFAULT NULL,
                            moonPhase VARCHAR(50) DEFAULT NULL,
                            PRIMARY KEY (dayId))"""

            cursor.execute(sqltb_u)
            cursor.execute(sqltb_ob)
            cursor.execute(sqltb_f)
            cursor.execute(sqltb_wd)
            return render_template('_home.html')
        except Exception as e:
            print(e)
        finally:
            print("conn, cursor:", conn)

# [end] --------------------
	

# =====================================================================
#         SHOW TABLES
# =====================================================================
@app.route('/all_users')
def show_users():
        try:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            table = Results(rows)
            table.border = True
            return render_template('users.html', table=table)
        except Exception as e:
            print(e)

@app.route('/all_files')
def show_files():
        try:
            cursor.execute("SELECT * FROM files")
            rows = cursor.fetchall()
            table = ResultsFile(rows)
            table.border = True
            return render_template('files.html', table=table)
        except Exception as e:
            print(e)

@app.route('/all_obs')
def show_obs():
        try:
            cursor.execute("SELECT * FROM observations")
            rows = cursor.fetchall()
            table = ResultsObs(rows)
            table.border = True
            return render_template('observations.html', table=table)
        except Exception as e:
            print(e)

@app.route('/all_wd')
def show_wd():
        try:
            cursor.execute("SELECT * FROM weatherDaily")
            rows = cursor.fetchall()
            table = ResultsWD(rows)
            table.border = True
            return render_template('wd.html', table=table)
        except Exception as e:
            print(e)

# [end] --------------------


# =====================================================================
# ADDING NEW ATTRIBUTES
# =====================================================================

@app.route('/new_file')
def add_file_view():
        try:
            return render_template('addFile.html')
        except Exception as e:
            print(e)

@app.route('/new_user')
def add_user_view():
        try:
            return render_template('addUser.html')
        except Exception as e:
            print(e)

@app.route('/new_obs')
def add_obs_view():
        try:
            return render_template('addObs.html')
        except Exception as e:
            print(e)
	
@app.route('/new_wd')
def add_wd_view():
        try:
            return render_template('addWD.html')
        except Exception as e:
            print(e)
	
@app.route('/addUser', methods=['POST'])
def add_user():
	try:		
            _uid = request.form['inputUserId']
            _fname = request.form['inputFName']
            _lname = request.form['inputLName']
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']
            _permissions = request.form['inputPermissions']
	    # validate the received values
            if (_uid and _lname and _email and _password and request.method == 'POST'):
                #do not save password as a plain text
                _hashed_password = generate_password_hash(_password)
		# save edits
                sql = "INSERT INTO users (userId, password, firstName, lastName, email, permissions) VALUES (%s, %s, %s, %s, %s, %s)"
                data = (_uid, _hashed_password, _fname, _lname, _email, _permissions)
                cursor.execute(sql, data)
                conn.commit()
                flash('User added successfully!')
                return redirect('/all_users')
            else:
                return 'Error while adding user'
	except Exception as e:
            print(e)


@app.route('/addFile', methods=['POST'])
def add_file():
        print(" add_file ")
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
                #do not save password as a plain text
		# save edits
                sql = "INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (_fid, _oname, _gid, _reds, _fileType, _bandType, _quality, _position, _date, _time, _timeStamp)
                print(" ADDFILE ::")
                print(sql,data)
                cursor.execute(sql, data)
                conn.commit()
                flash('File added successfully!')
                return redirect('/all_files')
            else:
                return 'Error while adding File'
        except Exception as e:
            print(e)
	
@app.route('/addObs', methods=['POST'])
def add_obs():
        print(" add_obs ")
        try:
            _gid = request.form['inputGroupId']
            _fid = request.form['inputFileId']
            _start = request.form['inputStart']
            _end = request.form['inputEnd']
            # validate the received values
            if (_fid and _gid  and request.method == 'POST'):
                #do not save password as a plain text
		# save edits

                sql = "INSERT into observations (groupId, fileId, startTime, endTime) values(%s, %s, %s, %s)"
                data = (_gid, _fid, _start, _end)
                cursor.execute(sql, data)
                conn.commit()
                flash('Observation added successfully!')
                return redirect('/all_obs')
            else:
                return 'Error while adding Observation'
        except Exception as e:
            print(e)
	
	
@app.route('/addWD', methods=['POST'])
def add_wd():
        print(" add_wd ")
        try:
            _date = request.form['inputDate']
            _rise = request.form['inputRise']
            _down = request.form['inputDown']
            _moon = request.form['inputMoon']
            # validate the received values
            if (_date and _down  and _moon and request.method == 'POST'):
                #do not save password as a plain text
		# save edits
                sql = "INSERT into weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) values(%s, %s, %s, %s)"
                data = (_date, _rise, _down, _moon)
                print("inside addWD: ", sql, data)
                cursor.execute(sql, data)
                conn.commit()
                flash('Day Weather added successfully!')
                return redirect('/all_wd')
            else:
                return 'Error while adding Day Weathere'
        except Exception as e:
            print(e)
	

@app.route('/edit/<string:id>')
def edit_view(id):
	try:
            cursor.execute("SELECT * FROM users WHERE userId=%s", id)
            print("editU userid = %s", id)
            row = cursor.fetchone()
            if row:
                return render_template('edit.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)

@app.route('/editO/<string:id>')
def edit_obs_view(id):
	try:
            print("editO fileid = %s", id)
            cursor.execute("SELECT * FROM observations WHERE fileId=%s", id)
            row = cursor.fetchone()
            if row:
                return render_template('editObs.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)


@app.route('/editF/<string:id>')
def edit_file_view(id):
	try:
            print("editF fileid = %s", id)
            cursor.execute("SELECT * FROM files WHERE fileId=%s", id)
            row = cursor.fetchone()
            if row:
                return render_template('editFile.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)


@app.route('/editWD/<string:id>')
def edit_wd_view(id):
	try:
            print("editWD dayId = %s", id)
            cursor.execute("SELECT * FROM weatherDaily WHERE dayId=%s", id)
            row = cursor.fetchone()
            if row:
                return render_template('editWD.html', row=row)
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
                if (_lname and _email and _password and _uid and request.method == 'POST'):
                    #do not save password as a plain text
                    _hashed_password = generate_password_hash(_password)
                    print(_hashed_password)
                    # save edits
                    sql = "UPDATE users SET userId=%s, password=%s, firstName=%s, lastName=%s, email=%s WHERE userId=%s"
                    data = (_uid, _hashed_password, _fname, _lname, _email, _permissions, _uid,)
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute(sql, data)
                    conn.commit()
                    flash('User updated successfully!')
                    return redirect('/all_users')
                else:
                    return 'Error while updating user'
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
                    data = (_fid, _oname, _gid, _reds, _fileType, _bandType, _quality, _position, _date, _time, _timeStamp)
                    cursor.execute(sql, data)
                    conn.commit()
                    flash('File updated successfully!')
                    return redirect('/all_files')
                else:
                    return 'Error while updating file'
	except Exception as e:
            print(e)
		

@app.route('/deleteU/<string:id>')
def delete_user(id):
	try:
		cursor.execute("DELETE FROM users WHERE userId=%s", (id,))
		conn.commit()
		flash('User deleted successfully!')
		return redirect('/all_users')
	except Exception as e:
		print(e)

@app.route('/deleteF/<string:id>')
def delete_file(id):
	try:
		cursor.execute("DELETE FROM files WHERE fileId=%s", (id,))
		conn.commit()
		flash('File deleted successfully!')
		return redirect('/all_files')
	except Exception as e:
		print(e)
		
if __name__ == "__main__":
    app.run()
