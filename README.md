# Web Fits Viewer
An online server to show FITS images and other data. A demo viewer with sample data is at
[hawcnest.ciera.northwestern.edu/viewdemo](https://hawcnest.ciera.northwestern.edu/viewdemo).

**Table of Contents:**
  * [Users Manual](#userman)
  * [Installation Manual](#instman)
  * [Developper's Manual](#devman)
  * [Support](#support)
    * [Installation Solutions](#support_install)

<a name="userman"></a>
## Users Manual

The Options at the top show you the different screens:
 * The first option (File Set / AOR List in the demo) links to a list of folders / subfolders with FITS files to look at.
 * Data Viewer: gives you access to view the data (you can still select different folders)
 * Pipeline Log: Shows you the log for reducing the data shown in the viewer (details may differ on how the Web Fits Viewer was insatlled)
 * Help / Manual: Links to this document or another manual.

<a name="instman"></a>
## Installation Manual

  * Download the code in webfitsviewer
  * Make sure the webserver (Apache or Tomcat) has read and execute (where needed) access to the files in webfitsviewer
  * Make your own copy of the server configuration file webfitsview_apache.conf and the viewer configuration file webfitsview_config.txt .
  * Edit your copies of these files to point to the correct files.
  * Setup the webserver with the config file (webfitsview_apache.conf or your own version of it). Restart your webserver.
  * Now, you should be able to see the page at [127.0.0.1/webview](http://127.0.0.1/webview). Subtitute the domain name of your server if you're working remotely. 

<a name="devman"></a>
## Developper's Manual

Read the code

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
    * This usually means loading cgid_module. 
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
