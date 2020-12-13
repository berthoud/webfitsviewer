# Web Fits Viewer
An online server to show FITS images and other data. A demo viewer with sample data is at
[hawcnest.ciera.northwestern.edu/viewdemo](https://hawcnest.ciera.northwestern.edu/viewdemo).

**Table of Contents:**
  * [Users Manual](#userman)
  * [Installation Manual](#instman)
  * [Developper's Manual](#devman)
  * [Support](#support)
    * [Installation Solutions](#support_install)
    
The purpose of the Web Fits Viewer is to allow the users to quickly look through imaging data without having to download the files. The Web Fits Viewer also allows rudimentary image analysis and has a modular architecture to facilitate extentions. 

<a name="userman"></a>
## Users Manual

The Options at the top show you the different screens:
 * The first option (File Set / AOR List in the demo) links to a list of folders / subfolders with FITS files to look at.
 * Data Viewer: gives you access to view the data (you can still select different folders)
 * Pipeline Log: Shows you the log for reducing the data shown in the viewer (details may differ on how the Web Fits Viewer was insatlled)
 * Help / Manual: Links to this document or another manual.

<a name="instman"></a>
## Installation Manual

  * Download the code from github.
  * Make your own copy of the server configuration file webfitsview_apache.conf and the viewer configuration file webfitsview_config.txt .
    * Edit your copies of these files to point to the correct files and folders.
    * Update other configuration items to fit your requirements.
  * Make sure the webserver (Apache or Tomcat) has read and execute (where needed) access to the files in webfitsviewer
  * Setup the webserver with the config file (webfitsview_apache.conf or your own version of it). Restart your webserver.
  * Now, you should be able to see the page at [127.0.0.1/webview](http://127.0.0.1/webview). Subtitute the domain name of your server if you're working remotely. 

<a name="devman"></a>
## Developper's Manual

The webserver serves pages and accesses the database using python scripts that are run by an apache webserver. Screenshot (click to enlarge):

![Web Fits View Screenshot](https://raw.githubusercontent.com/berthoud/webfitsviewer/database_dev/docs/images/WebViewScreenShot.png)

**URLs**

The basic url structure is

/baseurlpath/page/...possible.folders.../request

Examples: /hawcview/log/update or /seo2020/data/2020-07-01/M42

 * The request is optional (used for AJAX requests and such), absolute url paths are always used.
 * For auxiliary files the url path is /baseurlpath/folder/file (ex: /hawcview/static/style.css).
 * The different pages can be accessed using the links at the top of the page.
   * /hawcview/list/dataset: This page displays a list of all the different datasets and subsets available. /hawcview defaults to that page.
   * /hawcview/data/dataset/subset : The page to access the data.
     * /hawcview/data/dataset/subset/raw : AJAX request for the data. The data is returned as a list of keywords followed by the data itself.
     * The dataset/subset folders are optional as the server uses the stored session ID for most requests.
   * /hawcview/log : The page that displays the pipeline log. This page gets reloaded several times a minute (set in config).
     * /hawcview/log/update: AJAX request for new log entries. This request uses the loglevel and logtime session variables.
   * /hawcview/error : The page that gets called if an error happens. Though mostly errors in the python code create a page that shows a python traceback.
   * /hawcvew/test: This page runs tests on the server and to confirm browser compatibility.

**Web Application**

The application can connect to the server in WSGI. Currently we use the wsgiref.handlers.CGIHandler and run the application.
 * General user settings are remembered using cookies
 * Each browser window / tab is a session, the session id is POSTed with hidden inputs in forms. Sessions are stored on the server using the shelve module. The session contains the following information:
   * Session ID: Unique identifier SAH1(time of first request with client IP)
   * Page: Which page is requested (data/log/list . . .)
   * Request: The current AJAX request
   * Folder: Folder/SubFolder with files to be looked at (with HAWC Flight/AOR)
   * File: Selected file to view. A combination of filenamebegin and filenameend
   * Step: Pipeline reduction step to view
   * Data: Which HDU (or header for primary header) to view
   * Plane: Which plane to view for data cubes
   * Loglevel: Which level to show for pipeline log view
   * Logtime: Time of the last log entry that was passed to the client
   * Listfoler: Mainfolder that is showing at the top of the list of datasets and subsets
 * At a later time we will use mod_wsgi to improve server performance.
   
**Folders and File Structure**

 * Folders:  static (images, css, js), src (a module with controller.py, model.py, views.py main.py), filedata (the database), logs (with log files), temp (with images and sessions subfolders), config (with configuration files)
 * The configuration files are:
   * hawcview.conf: Apache configuration, contains the alias to the main script and aliases to the various folders. A hawcview.conf can link to several webviewer instances.
   * pipe_conf_webview.txt: configuration for pipedata object
   * webview_config.txt: configuration for the web interface
   * weblog_config.txt: configuration for the logging of the web interface.

**Code Architecture**
 * main.py: is called by the server. Contains the WSGI wrapper and calls controller object. (warning) This file has to be different for each instance of the webviewer.
 * controller.py: contains application that does the following:
   * Load configuration, set up logging, retrieve cookies and session - check them (by using the model) - set them
   * Get the request and retrieve and set the options for the request
   * Call start_response
   * Get the correct page from views and returns the page to the caller
 * views.py: contains functions that create text and return strings. The views object receives session information when it is initialized and uses the model object to access the data. Some pages require several commands to be built.
 * model.py: gives access to the data to the other objects. The model object receives session information when it is initialized. The model always has one pipedata object and only reloads it when necessary. The model also accesses the log from the pipeline.
 * When determining the request options (which folder / file / step . . .) POST parameters have precedence over request URI folders which has precedence over stored session values.
 
* search.py:
  * main program for search function. Currently, requires manual apache2 start

* app.py
  * attaches flask to project

* db_config.py
  * sets connection to mysql database. Requires password (TODO: change to use database_config.txt as reference for stars server user/password)

* forms.py
  * Formatting for flask forms are detailed here. The basic Search form is S_SearchForm (TODO: must change static to use column values listed in database_config.txt)

* tables.py
  * Flask tables are detailed here. The basic Search result provides names and values for all columns. (TODO: change static to use column values listed in database_config.txt; insert appropriate path links on the database to view single results)

* templates/_initdb.html
  * initializes connection to mysql. Quick call, html code is not seen.
  
* templates/_formhelpers.html
  * Contains flask formatting for forms.
  
* templates/results.html
  * Page displays results in a table after Search.py calls to form = search.

* templates/queries.html
  * allowed query display

* templates/index.html
  * Page to display search form and handle input values for simple query.

* templates/files.html
  * Page displays all files listed in table format. (TODO: replace reference)

* templates/addFile.html
  * TODO: Read permissions first.



**Configuration Format**

The configuration options are in the configuration file which is loaded as a config object by the controller object.
 * Path options:
   * basepath: path to the base folder
   * baseurlpath: url path common to all pages
   * session: path to the session folder
   * images: path to the images folder
   * static: path to the static folder
   * datapath: path to the filedata folder
   * dataurlpath: url path to the filedata folder
   * pipelog: absolute path to the pipeline log file
 * Controller options:
   * logconfig: path and name of the log configuration file
   * debuginfo: flag indicating if debug information to be shown in the rendered page
 * View options:
   * helpurl: url to the help page
   * foldernames: names the user sees to designate folders at a certain level (Ex: Flight/AOR for HAWC)
   * Data options
     * stepnames: list with acronyms and names for the data reduction steps
     * infolist: list of the header information to be shown in the info window
     * maxsize: maximal image size
   * Dataset list options
     * listkeyw: list of FITS keywords to be shown in the list of flights and aors
     * listfoldern: minimal number of folders shown in list view
     * listsubfoldern: minimal number of subfolders shown in list view
   * Log options
     * logreloadtime: number of seconds until the log file view gets updated
 * Model options:
   * pipeconf: path and name of the pipeline configuration file to be used for initializing pipe objects
   * minsize: minimal size of displayed images in pixels
   * maxsize: maximal image dimension
   * steporder: order in which data reduction steps should be listed (by acronym)


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
1) Using the commandline, enter directory: **$ cd /webviewer/webviewer**
2) Change mysql login credentials on **db_config.py** to yours.
3) Using the commandline, run program: **$ python main.py**
4) Open browser, go to url: http://localhost:5000/
5) Explore!

<a name="support"></a>
## Support
Use the wiki or contact @berthoud

<a name="support_install"></a>
### Installation Solutions
If you encounter problems, change the server configuration file ( .conf ) to run testmain.py instead of main.py.
To do that you uncomment the appropriate ScriptAlias.
  * **No change in webserver behavior:** You updated the .conf file but nothing changed.
    * Make sure the changes you made are in the config file that the webserver is actually using.
    * Restart your webserver after configuration changes. ex: apachectl restart
    * Consult the webserver error log for more information.
      * On mac: /var/log/apache2 or similar folder.
      * On windows: C:\Users\you\Documents\apacheServer\Apache24\logs
  * **Unable to connect** error from your browser.
    * Your web server may be shut down or not have restarted correctly. 
    * Go to [127.0.0.1](http://127.0.0.1) as most webservers have a default splash page.
    * Undo the configuration changes and restart the webserver.
  * **Webserver doesn't start:** You install the .conf file and after restarting the webserver (apache) you don't get a page.
    * You may have to replace "Require all access" with "Requre local" in the configuration file.
  * **Browser reports "Forbidden"** or webserver log reports **Permission denied: exec** of main.py
    * Make sure the webserver user on your machine has read and execute access to this file.
  * Browser shows **content of main.py** file, it doesn't run the file
    * Make sure your main server configuration (usually httpd.conf) allows running cgi scripts.
    * This usually means loading and enabling cgid_module. 
    * For apache look at [
  * **Wrong python version is used:** the webserver doesn't run the python installation you expect.
    * Use SetEnv PATH "/opt/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" in your webserver configuration path.
    * Edit the first line in main.py (or testmain.py) to say "python3" instead of "python"
  * **Unable to load configuration file:** You make a change to the configuration file now the application doesn't load.
    * Review the changes you made to the configuration file, check for syntax errors
    * Run the following code in a shell and check for any error messages.
```python
from configobj import ConfigObj
conffilename = '/path/file/name/of/your/webfitsview_config.txt'
conf = ConfigObj(conffilename)
```
