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
