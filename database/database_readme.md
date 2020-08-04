# WELCOME TO STARS-DB

**Table of Contents:**
  * [Initial Database Code](#idb)
    * [Run Initial Database Guide](#idbrun)
    * [Testing Support Guide](#idb_tst)
  * [Database Webview](#webdb)
    * [Webview Installation Guide](#webin)
    * [Run Webview Guide](#webrun)
    * [Testing Support Guide](#web_tst)

--------------------

<a name="idb"></a>
## INITIAL DATABASE CODE

<a name="idbrun"></a>
### To run, you need to...
1) have mysql installed and the server running. You can download this [here](https://dev.mysql.com/downloads/). I believe you only need the community server and the connector/python, although I think you can also just get the connector/python using pip. If you need an archival version, after selecting "community sever" on the linked page, click "archives" and then select a "product" version far back enough that it is compatible with your OS. (It will give the OS version for each product version you're viewing.)
2) have the requirements listed in requirements.txt. You should be able to get these by just installing astropy and mysql-connector-pytthon. Make sure you don't accidentally install mysql-connector; the command should be "pip install mysql-connector-python". You may [run into there error described here](https://stackoverflow.com/questions/50557234/authentication-plugin-caching-sha2-password-is-not-supported) if you don't do this. (If you get that error despite having the right thing installed, try uninstalling and installing again; it worked for me.)
3) Go into create_database.py root password and data path (if you intend to test by adding files to the table). You may need to google around to figure out what the default root password is for your mysql sever. Note that the path_to_sample_data should be a directory that holds some FITS files and no files that are not FITS files. Optionally you can pass in your root password as a command line argument and the value in the file will be ignored.
# Usage
If you do all of the above, you should be able to run create_databases.py and it will 
1) create an seo database within your mysql server
2) create a fits_data table within that database, with fields described in fits_data_table_config.py
3) populate that seo table using the FITS files in path_to_sample_data. 
Note that repeated reruns will delete and recreate the table. I recommend reading the code and comments as alternatives are commented out sometimes, in particular with regards to deleting already existing things.

<a name="idb_tst"></a>
### SUPPORT: Testing
With regards to seeing the results from the code, I recommend just running mysql in the command line. After successfully running create_database.py, you can run the following sequence of commands to understand what occurred:

⋅⋅⋅ **$ mysql -u root -p** <will prompt you for root password>

⋅⋅⋅ **mysql> SHOW DATABASES;** <shows databases, should include the seo one the code creates>

⋅⋅⋅ **mysql> USE seo;** 

⋅⋅⋅ **mysql> SHOW TABLES;** <shows tables within seo, should include fits_data one created by code>

⋅⋅⋅ **mysql> DESC fits_data;** <should show fields of fits_data table>

⋅⋅⋅ **mysql>** **SELECT** * **FROM fits_data;** <should show records added from your path_to_data>

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
