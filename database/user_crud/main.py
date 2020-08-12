import pymysql
import mysql.connector
from app import app
from tables import Results, ResultsFile, ResultsObs, ResultsWD, SearchMoon, Results_Cq1, Results_Cq2, Results_Cq3, Results_Cq4, Results_Cq5, Results_Sq2
from db_config import mysql
from flask import Flask, flash, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from forms import S_SearchForm, Moon_SearchForm

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
            print("disconn:", conn)
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
        print("LOAD init")
        return render_template('_initdb.html')

@app.route('/restart')
def restart():
        print("*** deleted database ***")
        DROP_DB = """DROP DATABASE stars_db"""
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(DROP_DB)

        return redirect('/out')

@app.route('/populate')
def populate():
        clear_o = """DELETE FROM observations"""
        clear_u = """DELETE FROM users"""
        clear_w = """DELETE FROM weatherDaily"""
        clear_f = """DELETE FROM files"""

        o1 = """INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values('group-c', '2020-07-23', '08:07', '2020-07-26', '08:07', 'long test')"""
        o2 = """INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values('group-b', '2020-08-10', '19:52', '2020-08-11', '19:52', 'test')"""
        o3 = """INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values('group-a', '2020-08-03', '19:40', '2020-08-03', '22:30', 'test')"""
        o4 = """INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values('group-d', '2020-07-04', '10:40', '2020-07-05', '3:30', 'test Full')"""
        o5 = """INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values('group-z', '2020-07-04', '21:40:00', '2020-07-05', '1:19', 'idk')"""

        w1 = """INSERT INTO weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) VALUES ('2020-07-04', '6:29:00', '21:30:00', 'Full')"""
        w2 = """INSERT INTO weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) VALUES ('2020-07-20', '6:12:00', '21:13:00', 'New')"""
        w3 = """INSERT INTO weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) VALUES ('2020-07-23', '5:30:00', '20:30:00', '11')"""
        w4 = """INSERT INTO weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) VALUES ('2020-08-01', '5:32:00', '20:32:00','95')"""
        w5 = """INSERT INTO weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) VALUES ('2020-08-03', '6:31:00', '20:32:00', 'Full')"""

        u1 = """INSERT INTO users (userId, password, firstName, lastName, email, permissions) VALUES('user1', 'pbkdf2:sha256:150000$T7xLy0Yd$438c51bc5cc8bb04025a0b89c95349fb9255088ac5bf91539af34ffc45bbb715', 'User', 'One', 'user1@gmail.com', '11')"""
        u2 = """INSERT INTO users (userId, password, firstName, lastName, email, permissions) VALUES('user2', 'pbkdf2:sha256:150000$PUgroQZL$4fc99733743eb82e8a0058abacff2a5e16ec7ca90a2729c9b1dea67003b48fe4', 'User', 'Two', 'user2@gmail.com', '11')"""

        f1 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-a1', 'venus', 'group-a', 'size', 'FITS', 'clear', 'medium', '100', '2020-08-03', '21:48', 'timeNow')"""
        f2 = """INSERT into files (fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES ('file-a2', 'venus', 'group-a', 'full', 'FITS', 'clear', 'low', '20', '2020-08-03', '21:00', 'timeNow')"""
        f3 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-a3', 'venus', 'group-a', 'full', 'FITS', 'clear', 'medium', '20', '2020-08-03', '21:10', 'timeNow')"""
        f4 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-a4', 'venus', 'group-a', 'band', 'FITS', 'red', 'medium', '20', '2020-08-03', '21:15', 'timeNow')"""
        f4 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-c1', 'moon', 'group-c', 'band', 'FITS', 'clear', 'excellent', '70', '2020-07-21', '1:10', 'timeNow')"""
        f5 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-c2', 'moon', 'group-c', 'band', 'FITS', 'red', 'excellent', '70', '2020-07-21', '1:20', 'timeNow')"""
        f6 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-d1', 'mars', 'group-d', 'size', 'FITS', 'clear', 'low', '10', '2020-07-05', '1:30', 'timeNow')"""
        f7 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-d2', 'moon', 'group-d', 'size', 'FITS', 'clear', 'low', '10', '2020-07-04', '22:29', 'timeNow')"""
        f8 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-b2', 'moon', 'group-b', 'full', 'FITS', 'red', 'excellent', '30', '2020-07-23', '22:48', 'timeNow')"""
        f9 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-b3', 'mars', 'group-b', 'size', 'FITS', 'blue', 'low', '10', '2020-07-24', '3:30', 'timeNow')"""
        f10 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-b1', 'jupiter', 'group-b', 'align', 'FITS', 'green', 'excellent', '30', '2020-07-23', '21:43:30', 'timeNow')"""
        f11 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-b4', 'venus', 'group-b', 'size', 'FITS', 'clear', 'medium', '20', '2020-07-24', '5:30', 'timeNow')"""
        f12 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-c3', 'moon', 'group-c', 'band', 'FITS', 'green', 'medium', '70', '2020-07-21', '1:25', 'timeNow')"""
        f13 = """INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES('file-c4', 'moon', 'group-c', 'band', 'FITS', 'blue', 'excellent', '70', '2020-07-21', '1:10', 'timeNow')"""

        p_list = [o1,o2,o3,o4,o5, w1,w2,w3,w4,w5, u1,u2, f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13]
        cursor.execute(DISABLE_FK)
        cursor.execute(clear_o)
        cursor.execute(clear_u)
        cursor.execute(clear_w)
        cursor.execute(clear_f)
        for cmd in p_list:
            print("in loop cmd", cmd)
            cursor.execute(cmd)
            
        cursor.execute(ENABLE_FK)
        conn.commit()
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
        print("start = ", USE_DB)
        CREATE_DB = """CREATE DATABASE IF NOT EXISTS stars_db """
        USE_DB = """USE stars_db"""
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
                CHECK(firstName <> lastName),
                PRIMARY KEY (userid))"""

            sqltb_wd = """CREATE TABLE IF NOT EXISTS weatherDaily (
                            dayId DATE NOT NULL,
                            sunriseTime TIME DEFAULT NULL,
                            sundownTime TIME DEFAULT NULL,
                            moonPhase VARCHAR(50) DEFAULT NULL,
                            CHECK(sunriseTime<sundownTime),
                            PRIMARY KEY (dayId))"""


            sqltb_ob = """CREATE TABLE IF NOT EXISTS observations (
                groupId VARCHAR(255) NOT NULL,
                startDate DATE DEFAULT NULL,
                startTime TIME DEFAULT NULL,
                endDate DATE DEFAULT NULL,
                endTime TIME DEFAULT NULL,
                description VARCHAR(255) DEFAULT NULL,
                PRIMARY KEY (groupId),
                CONSTRAINT FK_ObsDay FOREIGN KEY (startDate) REFERENCES weatherDaily(dayId) ON UPDATE SET NULL ON DELETE SET NULL)"""


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
                PRIMARY KEY (fileId),
                CONSTRAINT CH_quality CHECK(quality IN ('low','medium','excellent')),
                CONSTRAINT CH_band CHECK(bandType IN ('all','red','green','blue','clear')),
                CONSTRAINT CH_reduction CHECK(reductionStage IN ('size','align','band','full')),
                CONSTRAINT FK_FileDay FOREIGN KEY (date) REFERENCES weatherDaily(dayId),
                CONSTRAINT FK_FileObs FOREIGN KEY (groupId) REFERENCES observations(groupId) ON UPDATE CASCADE ON DELETE CASCADE)"""


            #fk_FileObs = """ALTER TABLE files ADD CONSTRAINT FK_FileObs FOREIGN KEY (groupId) REFERENCES observations(groupId) ON UPDATE CASCADE ON DELETE CASCADE"""
            #fk_FileDate = """ALTER TABLE files ADD CONSTRAINT FK_FileDay FOREIGN KEY (date) REFERENCES weatherDaily(dayId)"""
            #fk_ObsWd = """ALTER TABLE observations ADD CONSTRAINT FK_ObsDay FOREIGN KEY (startDate) REFERENCES weatherDaily(dayId)"""
            cursor.execute(sqltb_u)
            cursor.execute(sqltb_wd)
            cursor.execute(sqltb_ob)
            cursor.execute(sqltb_f)
            #cursor.execute(fk_FileObs)
            #cursor.execute(fk_FileDate)
            #cursor.execute(fk_ObsWd)
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


# ====================================================================
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
                print(sql,data)
                cursor.execute(DISABLE_FK)
                cursor.execute(sql, data)
                cursor.execute(ENABLE_FK)
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
            if (_fid and _oname and _date and request.method == 'POST'):
                #do not save password as a plain text
		# save edits
                sql = "INSERT into files(fileId,objectName,groupId,reductionStage,fileType,bandType,quality,position,date,time,timeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data = (_fid, _oname, _gid, _reds, _fileType, _bandType, _quality, _position, _date, _time, _timeStamp)
                print(sql,data)
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
	
@app.route('/addObs', methods=['POST'])
def add_obs():
        print(" add_obs ")
        try:
            _gid = request.form['inputGroupId']
            _sd = request.form['inputSD']
            _st = request.form['inputST']
            _ed = request.form['inputED']
            _et = request.form['inputET']
            _desc = request.form['inputDesc']
            # validate the received values
            if (_sd and _gid  and request.method == 'POST'):
                #do not save password as a plain text
		# save edits
                cursor.execute(DISABLE_FK)
                sql = "INSERT into observations (groupId, startDate, startTime, endDate, endTime, description) values(%s, %s, %s, %s, %s, %s)"
                data = (_gid, _sd, _st, _ed, _et, _desc)
                print(sql, data)
                cursor.execute(sql, data)
                cursor.execute(ENABLE_FK)
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
                cursor.execute(DISABLE_FK)
                sql = "INSERT into weatherDaily (dayId, sunriseTime, sundownTime, moonPhase) values(%s, %s, %s, %s)"
                data = (_date, _rise, _down, _moon)
                print(sql, data)
                cursor.execute(sql, data)
                cursor.execute(ENABLE_FK)
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
            print("editO groupid = %s", id)
            cursor.execute("SELECT * FROM observations WHERE groupId=%s", id)
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
                if (_lname and _email and _uid and request.method == 'POST'):
                    #do not save password as a plain text
                    _hashed_password = generate_password_hash(_password)
                    print(_hashed_password)
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
		

@app.route('/updateO', methods=['POST'])
def update_O():
	try:
            _gid = request.form['inputGroupId']
            _sd = request.form['inputSD']
            _st = request.form['inputST']
            _ed = request.form['inputED']
            _et = request.form['inputET']
            _desc = request.form['inputDesc']
            
            # validate the received values
            if (_gid and _ed and request.method == 'POST'):
                # save edits
                sql = "UPDATE observations SET groupId=%s, startDate=%s, startTime=%s, endDate=%s, endTime=%s, description=%s WHERE groupId=%s"
                data = (_gid, _sd, _st, _ed, _et, _desc, _gid)
                cursor.execute(sql, data)
                conn.commit()
                flash('Observation updated successfully!')
                return redirect('/all_obs')
            else:
                return 'Error while updating observation'
	except Exception as e:
            print(e)

@app.route('/updateW', methods=['POST'])
def update_W():
        try:
            _date = request.form['inputDate']
            _rise = request.form['inputRise']
            _down = request.form['inputDown']
            _moon = request.form['inputMoon']
            
            if (_date and request.method == 'POST'):
                sql = "UPDATE weatherDaily SET dayId=%s, sunriseTime=%s, sundownTime=%s, moonPhase=%s WHERE dayId=%s"
                data = (_date,_rise,_down,_moon,_date)
                cursor.execute(sql, data)
                conn.commit()
                flash('Weather for day updated successfully!')
                return redirect('/all_wd')
            else:
                return 'Error while updating observation'
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
		flash('File deleted successfully!', 'success')
		return redirect('/all_files')
	except Exception as e:
		print(e)

@app.route('/deleteO/<string:id>')
def delete_obs(id):
	try:
		cursor.execute("DELETE FROM observations WHERE groupId=%s", (id,))
		conn.commit()
		flash('Observation deleted successfully!', 'success')
		return redirect('/all_obs')
	except Exception as e:
		print(e)
                
@app.route('/deleteW/<string:id>')
def delete_wd(id):
	try:
                cursor.execute(DISABLE_FK)
                cursor.execute("DELETE FROM weatherDaily WHERE dayId=%s", (id,))
                cursor.execute(ENABLE_FK)
                conn.commit()
                flash('Day deleted successfully!', 'success')
                return redirect('/all_wd')
	except Exception as e:
            print(e)
 
# =====================================================================
#         SIMPLE QUERIES :  
# =====================================================================
# 1: Search tables by primary key containing value
# 2: Show observations in order of Oldest to Latest
# 3: Show Day and moonphase 
@app.route('/sq_2')
def show_sq2():
        try:
            cursor.execute("SELECT * FROM observations ORDER BY startDate ASC")
            rows = cursor.fetchall()
            table = ResultsObs(rows)
            table.border = True
            flash('Search by primary id')
            return render_template('queries.html', table=table)
        except Exception as e:
            print(e)

@app.route('/sq_3_res')
def show_sq3(phase):
    results = []
    select_string = phase.data['select']
 
    if phase.data['select'] == '':
        flash('Empty search. Please try again!')
        return redirect('/sq_3')

    m_query = "SELECT dayId, moonPhase FROM weatherDaily WHERE moonPhase LIKE '%"+select_string+"%'"
    cursor.execute(m_query)
    results = cursor.fetchall() 
    if not results:
        flash('No results found!')
        return redirect('/sq_3')
    else:
        # display results
        table = SearchMoon(results)
        table.border = True
        return render_template('sq3.html', table=table)

# index
@app.route('/sq_3', methods=['GET', 'POST'])
def load_sq3():
    phase = Moon_SearchForm(request.form)
    if request.method == 'POST':
        return show_sq3(phase)
    return render_template('sq3_index.html', form=phase)


@app.route('/results')
def search_results(search):
    results = []
    select_string = search.data['select']
    search_string = search.data['search']
    sql_table = select_string 
    sql_col = ''

    if search.data['search'] == '':
        flash('Empty search. Please try again!')
        return redirect('/search')

    if select_string == 'Users' :
        sql_table == 'users'
        sql_col = 'userId'
    elif select_string == 'Day Weather':
        sql_table == 'weatherDaily'
        sql_col = 'dayId'
    elif select_string == 'Observations':
        sql_table == 'observations'
        sql_col = 'groupId'
    else:
        sql_table == 'files'
        sql_col = 'fileId'

    query = "SELECT * FROM "+sql_table+" WHERE "+sql_col+" LIKE '%"+search_string+"%'"
    cursor.execute(query)
    results = cursor.fetchall() 
    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results
        print("WORKED table =")
        if select_string == 'Users':
            print("table = RESULTS")
            table = Results(results)
        elif select_string == 'Observations':
            print("table = RESULTS OBS") 
            table = ResultsObs(results)
        elif select_string == 'Day Weather':
            print("table = RESULTS WD") 
            table = ResultsWD(results)
        else:
            print("table = RESULTS FILE")
            table = ResultsFile(results)

        table.border = True
        return render_template('results.html', table=table)

# index
@app.route('/search', methods=['GET', 'POST'])
def search_view():
    print("in SEARCH_VIEW")
    search = S_SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)


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





		
if __name__ == "__main__":
    app.run()
