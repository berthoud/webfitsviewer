import pymysql
from app import app
from tables import Results, ResultsFile
from db_config import mysql
from flask import flash, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/new_file')
def add_file_view():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            return render_template('addFile.html')
        except Exception as e:
            print(e)
        finally:
            cursor.close() 
            conn.close()

@app.route('/new_user')
def add_user_view():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            return render_template('addUser.html')
        except Exception as e:
            print(e)
        finally:
            cursor.close() 
            conn.close()


	
	
@app.route('/addUser', methods=['POST'])
def add_user():
	conn = None
	cursor = None
	try:		
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
 
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
                return redirect('/')
            else:
                return 'Error while adding user'
	except Exception as e:
            print(e)
	finally:
            cursor.close()
            conn.close()

@app.route('/addFile', methods=['POST'])
def add_file():
	conn = None
	cursor = None
	try:		
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
 
            _fid = request.form['inputFileId']
            _oname = request.form['inputObjectName']
            _date = request.form['inputDate']
            _time = request.form['inputTime']
            _timeStamp = 'timeNow' 
            _reds = request.form['inputReductionStage']
            _fileType = request.form['inputFileType']
            _quality = request.form['inputQuality']
            _position = request.form['inputPosition']
            _bandType = request.form['inputBandType']
	    # validate the received values
            if (_fid and _oname and _date  and request.method == 'POST'):
                #do not save password as a plain text
		# save edits
                sql = "INSERT into files(fileId,objectName,date,time,timeStamp,reductionStage,fileType,quality,position,bandType) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data = (_fid, _oname, _date, _time, _timeStamp, _reds, _fileType, _quality, _position, _bandType)
                cursor.execute(sql, data)
                conn.commit()
                flash('File added successfully!')
                return redirect('/')
            else:
                return 'Error while adding File'
	except Exception as e:
            print(e)
	finally:
            cursor.close()
            conn.close()
	

@app.route('/')
def init():
	conn = None
	cursor = None
	try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_init = """CREATE DATABASE IF NOT EXISTS stars_db """
            sql_start = """ USE stars_db """
            cursor.execute(sql_init)
            cursor.execute(sql_start)
            sqltb_u = """CREATE TABLE IF NOT EXISTS users (
                userId VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                firstName VARCHAR(50) DEFAULT NULL,
                lastName VARCHAR(50) DEFAULT NULL,
                email VARCHAR(100) DEFAULT NULL,
                permissions int(11) NOT NULL,
                PRIMARY KEY (userid))"""

            sqltb_f = """CREATE TABLE IF NOT EXISTS files (
                fileId VARCHAR(255) NOT NULL,
                objectName VARCHAR(50) DEFAULT NULL,
                            date DATE DEFAULT NULL,
                            time TIME DEFAULT NULL,
                            timeStamp VARCHAR(50) DEFAULT NULL,
                            reductionStage VARCHAR(50) DEFAULT NULL,
                            fileType VARCHAR(50) DEFAULT NULL,
                            quality VARCHAR(50) DEFAULT NULL,
                            position NUMERIC(5,3) DEFAULT NULL,
                            bandType VARCHAR(20) DEFAULT NULL,
                            PRIMARY KEY (fileId))"""

            sqltb_wd = """CREATE TABLE IF NOT EXISTS weatherDaily (
                            dayId DATE NOT NULL,
                            sunriseTime TIME DEFAULT NULL,
                            sundownTime TIME DEFAULT NULL,
                            moonPhase VARCHAR(50) DEFAULT NULL,
                            PRIMARY KEY (dayId))"""

            cursor.execute(sqltb_u)
            cursor.execute(sqltb_f)
            cursor.execute(sqltb_wd)
            return render_template('home.html')
	except Exception as e:
            print(e)
	finally:
            cursor.close() 
            conn.close()

@app.route('/all_users')
def show_users():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            table = Results(rows)
            table.border = True
            return render_template('users.html', table=table)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

@app.route('/all_files')
def show_files():
        conn = None
        cursor = None
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            cursor.execute("SELECT * FROM files")
            rows = cursor.fetchall()
            table = ResultsFile(rows)
            table.border = True
            return render_template('files.html', table=table)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()



@app.route('/edit/<string:id>')
def edit_view(id):
	conn = None
	cursor = None
	try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            cursor.execute("SELECT * FROM users WHERE userId=%s", id)
            print("editU userid = %s", id)
            row = cursor.fetchone()
            if row:
                return render_template('edit.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)
	finally:
            cursor.close()
            conn.close()

@app.route('/editF/<string:id>')
def edit_file_view(id):
	conn = None
	cursor = None
	try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql_start = """ USE stars_db """
            cursor.execute(sql_start)
            print("editF fileid = %s", id)
            cursor.execute("SELECT * FROM files WHERE fileId=%s", id)
            row = cursor.fetchone()
            if row:
                return render_template('editFile.html', row=row)
            else:
                return 'Error loading #{id}'.format(id=id)
	except Exception as e:
            print(e)
	finally:
            cursor.close()
            conn.close()


@app.route('/update', methods=['POST'])
def update_user():
	conn = None
	cursor = None
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
                    return redirect('/')
                else:
                    return 'Error while updating user'
	except Exception as e:
            print(e)
	finally:
            cursor.close()
            conn.close()
		
@app.route('/deleteU/<string:id>')
def delete_user(id):
	conn = None
	cursor = None
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM users WHERE userId=%s", (id,))
		conn.commit()
		flash('User deleted successfully!')
		return redirect('/')
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/deleteF/<string:id>')
def delete_file(id):
	conn = None
	cursor = None
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM files WHERE fileId=%s", (id,))
		conn.commit()
		flash('File deleted successfully!')
		return redirect('/')
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
if __name__ == "__main__":
    app.run()
