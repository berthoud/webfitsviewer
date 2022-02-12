# WELCOME TO STARS-DB

**Table of Contents:**
  * [Initial Database Code](#idb)
    * [Run Initial Database Guide](#idbrun)
    * [Testing Support Guide](#idb_tst)
  * [Step Add to Database](#stepadd)
  * [Remote Queries](#remotequeries)
  * [Database Webview](#webdb)
    * [Webview Installation Guide](#webin)
    * [Run Webview Guide](#webrun)
    * [Testing Support Guide](#web_tst)

--------------------

<a name="idb"></a>
## INITIAL DATABASE CODE: create_database.py

<a name="idbrun"></a>
### To run, you need to...
1) Have mysql installed and the server running. You can download this [here](https://dev.mysql.com/downloads/). I believe you only need the community server and the connector/python, although I think you can also just get the connector/python using pip. If you need an archival version, after selecting "community sever" on the linked page, click "archives" and then select a "product" version far back enough that it is compatible with your OS. (It will give the OS version for each product version you're viewing.)
2) Have the requirements listed in requirements.txt. You should be able to get these by just installing astropy and mysql-connector-python. Make sure you don't accidentally install mysql-connector; the command should be "pip install mysql-connector-python". You may [run into the error described here](https://stackoverflow.com/questions/50557234/authentication-plugin-caching-sha2-password-is-not-supported) if you don't do this. (If you get that error despite having the right thing installed, try uninstalling and installing again; it may work .)
3) Have setup the config file stored in database_config.txt 
4) Have access to an SQL user that can create a database, create tables, and populate them. Optionally, you may want the user able to create new users.

# create_database.py Usage
"python3 create_database.py -h" will describe the functionality of different command line arguments. Default values for non-boolean command line arguments are stored at the top of the create_database.py file and can be changed if you don't want to enter them. If you don't want to rely on any of the defaults and instead do want to enter them on the command line, the required arguments are -user, -pass, -configpath, and -dbname. Be wary of entering -pass on the command line. Note that -pass can be optionally a file path and the first line of the file will be parsed for the password.

The basic functionality without any optional command line arguments is to create a database and populate it with the tables described in the config file. Optional command line arguments allow you to specify if already existing tables should be overwritten, if phony data should be added as a test, if users described in the database_config should be created, and if users described in the database_config should overwrite already existing users (if users are being created).


<a name="idb_tst"></a>
### SUPPORT: Testing
With regards to seeing the results from the code, I recommend just running mysql in the command line. After successfully running create_database.py, you can run the following sequence of commands to understand what occurred. This assumes that the default db_name and database config are used ('seo' and just a single 'fits_data' table).

⋅⋅⋅ **$ mysql -u root -p** <will prompt you for root password>

⋅⋅⋅ **mysql> SHOW DATABASES;** <shows databases, should include the seo one the code creates>

⋅⋅⋅ **mysql> USE seo;** 

⋅⋅⋅ **mysql> SHOW TABLES;** <shows tables within seo, should include fits_data one created by code>

⋅⋅⋅ **mysql> DESC fits_data;** <should show fields of fits_data table>

⋅⋅⋅ **mysql>** **SELECT** * **FROM fits_data;** <should show records added from your path_to_data>


## Database Config Format
The database config file is an ini file as used by the python package configobj, which allows nested sections. Currently, two outermost sections are supported. 

The first is \[tables\], within which each subsection is the name of a table. Within each table subsection are key value pairings, where the keys are the SQL table column names, and the values are the corresponding SQL types. There is additionally a required 'primary_key' field that maps to the SQL table column name of the primary key.

(For tables for FITS files, it is recommended to follow a naming convention mapping the FITS field name to a corresponding SQL field name. Such a convention is described in the config file.)

The second supported outermost section is \[users\]. Each subsection of this section describes a new user, although the name of the subsection itself isn't used at all and can just be chosen to be descriptive of the usage of that user. Each user is required to have a 'username' field, a 'pass' field, and a 'host' field (you probably just want localhost; this is where the user can log in from). Optionally, a 'SELECT' and/or 'INSERT' field can be added and set to 'True' or 'False. If it is added and set to 'True', the user will be granted those permissions for tables within the database created by create_database.py. Not adding is the same as setting to False.

Be wary about creating new users because you must manually delete them if you don't want them anymore.
--------------------

<a name="stepadd"></a>
## STEP ADD TO DATABASE
This section needs to be further filled out, but for now it should just be noted that the support for parsing different types within StepAddToDatabase is very limited as of now. For instance, date objecsts are not created.

--------------------
<a name="remotequeries"></a>
## Remote Queries
-Returns as JSON
--------------------


<a name="webdb"></a>
## DATABASE (CRUD) WEBVIEW
(Recycled/repurposed code from [source](https://www.roytuts.com/python-web-application-crud-example-using-flask-and-mysql/).)

<a name="webin"></a>
### Requirements & Installation
Pre-requisites: **Python 3.8.0, Flask 1.1.1, Flask Table 0.5.0, MySQL 8.0.17**

The module **table** is required to show data in tabular format on HTML view, the module **flask** works as a web framework and **mysql** module is required to establish connection with MySQL database and query the database using Python programming language.
 
⋅⋅⋅ **$ pip install flask_table**
 
⋅⋅⋅ **$ pip install flask-mysql**

<a name="webrun"></a>
### To run...
1) Using the commandline, enter directory: **$ cd user_crud**
2) Change mysql login credentials on **db_config.py** to yours.
3) Using the commandline, run program: **$ python main.py**
4) Open browser, go to url: http://localhost:5000/
5) Explore!

<a name="web_tst"></a>
### SUPPORT: Testing /Broken Code
 * If broken links to 'Show Users' or 'Show Files', click on 'Show Init' and try again.
 * Currently, the edit and delete functionalities do not work properly. Ultimately, these functions will not be available through the webviewer and will be exclusive to STARS server IP.

--------------------
Feel free to reach out if you run into problems.
