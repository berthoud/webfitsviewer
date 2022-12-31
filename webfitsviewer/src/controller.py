""" CONTROLLER.PY
    The site controller controlls the production of the response
    for requests to the website. The controller creates and interacts
    with both, the SiteModel and the SiteViews. A call to the controller
    calls start_response and returns the contents of the response.
    
    Upgrade to multi-site:
    ./ set up with config in apache config
    ./ changes to main
      ./ read and open config
      ./ set paths from config
      ./ check if import weberror works else set flag
    ./ changes to controller
      ./ look for script_name split into sitename and responsearr
        (keep older code arround but commented out)
      ./ update config if section with name exists
      ./ clean up baseurlpath or replace with siteurl where appropriate
    ./ test on current site
      ./ make 2 sites with 2 different folders and names (also check if basename works)
      ./ also check if old system with scriptalias still works
    ./ changes to main with extra error
      ./ make changes to have both error functions, call of correct application at bottom
      ./ test both errors
    - look at main <-> controller: does split make sense?
    - update log in controller
    
    Add search tab
    
    
"""

### Preparation
# Import
import sys # System Library
import os # OS Library
import time # Time Library
import logging.config # Logging Config Object
#import urlparse # URLParse Library (should be used instead of CGI)
#import cgi # CGI library (needed because urlparse.parse_qs broken in py2.5)
# Import parse_qs from cgi else from urllib.parse (as of py3.10)
try:
    from cgi import parse_qs
except:
    from urllib.parse import parse_qs
import hashlib # Hashlib Library
import shelve # Shelve Module
from configobj import ConfigObj # Configuration Object
from views import SiteViews # Site Views Object
from model import SiteModel # Site Model Object

class SiteController(object):
    """ Controller object that formulates the response to the http
        request.
    """
    def __init__(self):
        """ Constructor: declares the variables
        """
        # Declare Variables
        self.env = {'No Env':0} # Environment
        self.conf = None # Configuration Object
        self.output = 'No Output' # Output
        self.log = None # Logging Object
        self.sid = '' # Session ID
        self.session = {} # Session Variables
        self.request = {} # Request Variables
        self.views = None # The views object
        self.model = None # The model object

    def __call__(self,environ,start_response):
        """ Object Call: creates the response
        """
        ### Setup / Preparation
        errormsg = ''
        # Set Environment
        self.env = environ
        # Split URI into sitename and RESPONSEARR with path info -> fill / update session vars
        # response = environ.get('PATH_INFO','list') # Old code: PATH_INFO not available using SciptAliasMatch
        #responsearr = environ.get('SCRIPT_NAME').strip('/').split('/') # Does not work with older browsers
        responsearr = environ.get('REQUEST_URI').strip('/').split('/')
        if len(responsearr) > 0:
            siteurl = responsearr[0]
            responsearr = responsearr[1:]
        else: siteurl = ''
        # Load Configuration
        self.conf = ConfigObj(environ.get('WEBVIEW_CONFIG'))
        # Add configuration from site_sitename
        if 'site_'+siteurl in self.conf:
            self.conf.merge(self.conf['site_'+siteurl])
        # Edit siteurl in config
        if len(siteurl):
            self.conf['path']['siteurl'] = '/'+siteurl
        # Set up logging & print message
        logfile = os.path.join(self.conf['path']['basepath'],
                               self.conf['ctrl']['logfile'])
        logging.basicConfig(level='DEBUG',filename = logfile,
                            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('webview.control')
        self.log.info('********* Started Controller')
        self.log.info('          Request from %s to %s'
                       % (environ.get('REMOTE_ADDR'),
                          environ.get('REQUEST_URI')))
        # Get Post request parameters (decode if needed)
        try:
            request_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_size = 0
        request_body = environ['wsgi.input'].read(request_size)
        try:
            request_body = request_body.decode()
        except(UnicodeDecodeError,AttributeError):
            pass
        #request_params = cgi.parse_qs(request_body)
        request_params = parse_qs(request_body)
        # Attach GET request parameters
        query_string = environ['QUERY_STRING']
        #request_params.update(cgi.parse_qs(query_string))
        request_params.update(parse_qs(query_string))
        self.request = request_params
        # Get session id from Post request
        self.log.debug('Request Params = ' + repr(request_params))
        self.sid = request_params.get('sid',[''])[0]
        if len(self.sid):
            self.log.info('Existing Session SID = %s' % self.sid)
        else:
            self.log.info('New Session')
            self.sid = hashlib.sha1((repr(time.time())+environ['REMOTE_ADDR']).encode('utf-8')).hexdigest()
        # Get session information / make new session file
        sessionfile = os.path.join(self.conf['path']['basepath'],
                                   self.conf['path']['session'],
                                   'sess_%s' % self.sid)
        self.session = shelve.open(sessionfile, writeback = True)
        self.session['sid'] = self.sid
        # Make other objects
        self.views = SiteViews(self.env, self.session, self.conf)
        self.model = SiteModel(self.env, self.session, self.conf)
        self.views.model = self.model
        ###### Compute response (format is page/request)
        # Select Response and Query from URI -> fill / update session vars
        if len(responsearr) > 0:  self.session['page'] = responsearr[0].lower()
        else: self.session['page'] = 'list'
        if not (self.session['page'] in ['data','error','log', 'list', 'search', 'test']):
            self.session['page'] = 'list'
        self.log.info('Page Type is = %s' % self.session['page'])
        #-- DATA Response: update session variables and validate request
        self.session['request'] = '' # Clear request
        if self.session['page'] == 'data':
            responsefolder = '' # variable to allow check if folder is valid
            # Get and Validate request
            if responsearr[-1].lower() in ['raw']:
                self.session['request'] = responsearr[-1].lower()
                responsearr = responsearr[0:-1]
            # FOLDER selection from request parameters or response path array
            if 'folder_selection' in request_params:
                self.session['folder'] = request_params.get('folder_selection')[0]
            elif len(responsearr) > 1:
                responsefolder = os.path.join(*responsearr[1:])
                self.session['folder'] = responsefolder
            # FILE selection from request parameters
            if 'file_selection' in request_params:
                self.session['file'] = request_params.get('file_selection')[0]
            # STEP selection from request parameters
            if 'step_selection' in request_params:
                self.session['step'] = request_params.get('step_selection')[0]
            # DATA selection from request parameters
            if 'data_selection' in request_params:
                self.session['data'] = request_params.get('data_selection')[0]
            # PLANE selection from request parameters
            if 'plane_selection' in request_params:
                self.session['plane'] = request_params.get('plane_selection')[0]
            # Validate / Set session variables
            self.model.set_selection()
            # if no data available -> error
            if len(self.session['data']) == 0:
                self.session['page'] = 'error'
                errormsg = 'No FITS data avaialable:<br> &nbsp;'
                errormsg += ' folder = <%s>' % (self.session['folder'])
                errormsg += ' file = <%s>' % (self.session['file'])
                errormsg += ' step = <%s>' % (self.session['step'])
                errormsg += ' data = <%s>' % (self.session['data'])
                errormsg += ' plane = <%s>' % (self.session['plane'])
            # if responsefolder was invalid raise error
            if ( len(responsefolder) and not responsefolder in self.session['folder'] and
                 int(self.conf['ctrl']['erronbadurl']) ):
                self.session['page'] = 'error'
                errormsg = 'Nonexistent or empty folder requested: %s is not available or contains no data' % responsefolder
        #-- LOG Response: update session variables and validate request
        if self.session['page'] == 'log':
            # Get and Validate request
            if responsearr[-1].lower() in ['update']:
                self.session['request'] = responsearr[-1].lower()
            # LOG_LEVEL selection from request parameters
            if 'log_level' in request_params:
                level = request_params.get('log_level')[0]
                if level in 'DEBUG INFO WARNING ERROR CRITICAL':
                    self.session['loglevel'] = level
            elif not 'loglevel' in self.session:
                self.session['loglevel'] = 'INFO'
        #-- LIST Response: update session variables and validate request
        if self.session['page'] == 'list':
            # LIST_FOLDER selection from response path array
            responsefolder = '' # variable to allow check if folder is valid
            if len(responsearr) > 1:
                responsefolder = responsearr[1]
                self.session['listfolder'] = responsefolder
            else:
                self.session['listfolder'] = ''
            # Get Folder list and make sure there's something there
            folderlist = self.model.folderlist(0)
            if len(folderlist) == 0:
                self.session['page'] = 'error'
                errormsg = '<b>NO Data Folders Available</b><p> No folders were found under '
                errormsg += os.path.join(self.conf['path']['basepath'], self.conf['path']['datapath'])
                errormsg += '. Check the server settings or contact the administrator.'
            elif ( len(responsefolder) and not responsefolder in folderlist and 
                   int(self.conf['ctrl']['erronbadurl'])):
                self.session['page'] = 'error'
                errormsg = 'Nonexistent folder requested: %s is not available or contains no data' % responsefolder
            else:
                # Set list_folder            
                if not self.session['listfolder'] in folderlist:
                    self.session['listfolder'] = folderlist[-1]
        #-- TEST Response: log the messages
        if self.session['page'] == 'test':
            if 'messagetext' in request_params:
                self.log.debug('Test - Message from %s: %s' % 
                               (environ.get('REMOTE_ADDR'), request_params['messagetext'][0]) )
        # Print request if it came up
        if len(self.session['request']) > 0:
            self.log.info('Request Type is = %s' % self.session['request'])
        ###### Make response page
        # Initialize Response
        status = '200 OK'
        response_headers = [('Content-Type','text/html')]
        self.output = ''
        # If there is no request -> return regular page
        if len(self.session['request']) == 0 or self.session['page'] == 'error':
            # Create Response Header
            self.output += self.views.header()
            # Create Text
            if self.session['page'] == 'data':
                # Request is to see data
                self.output += self.views.data()
            elif self.session['page'] == 'error':
                # Request is an Error
                self.output += self.views.error(errormsg)
            elif self.session['page'] == 'log':
                # Request is log
                self.output += self.views.pipelog()
            elif self.session['page'] == 'list':
                # Request is list
                self.output += self.views.folderlist()
            elif self.session['page'] == 'search':
                # Request is search
                self.output += self.views.search()
            elif self.session['page'] == 'test':
                # Request is test
                self.output += self.views.test()
            # Close Response
            self.log.debug('debuginfo = %d' % int(self.conf['ctrl']['debuginfo']) )
            if( int(self.conf['ctrl']['debuginfo']) > 0 or
                self.session['page'] == 'test' ):
                self.list_env()
            self.output += '</body></html>'
        # If there is a querry -> return request text instead
        else:
            # Data, Raw request
            if self.session['page']+'-'+self.session['request'] == 'data-raw':
                self.output += self.views.dataraw()
            # Logging, Update request
            if self.session['page']+'-'+self.session['request'] == 'log-update':
                self.output += self.views.logupdate()
        # Return
        start_response(status, response_headers)
        self.log.info('********* Finished Controller')
        return self.output

    def list_env(self):
        """ Creates a response containing path and environment variables.
        """
        # Initialize Output
        output = "<hr>\n <h2>Environment Setup</h2>\n"
        # Add request text
        reqtext = ['<li>%s: %s' % (key, self.request[key])
                   for key in self.request]
        reqtext = '\n'.join(reqtext)
        output += '<b>Request:</b><ul>\n' + reqtext + '</ul>\n'
        # Add current path
        output += '<b>Current Path:</b> %s<p>\n' % os.getcwd()
        # Add session variables
        sesstext = ['<li>%s: %s' % (key, self.session[key])
                   for key in self.session]
        sesstext = '\n'.join(sesstext)
        output += '<b>Session Variables:</b><ul>\n' + sesstext + '</ul>\n'
        # Add environment Variables
        envstr = ['<li>%s: %s' % (key,self.env[key])
                  for key in sorted(self.env.keys())]
        envstr = '\n'.join(envstr)
        output += '<b>Environment Variables:</b><ul>\n' + envstr + '</ul>\n'
        # Add path
        pathstr = ['<li>%s' % p for p in sorted(sys.path) ]
        pathstr = '\n'.join(pathstr)
        output += '<b>Path Settings:</b><ul>\n' + pathstr + '</ul>\n'
        # Return answer
        self.output += output

""" === History ===
    2021-4 Marc Berthoud, remove use of logconfig
    2020 Marc Berthoud, Upgrade to multi-site
    2020-1-10 Marc Berthoud,
        * removed [path][baseurlpath from config: Either use absolute paths
          or use siteurl (which is set automatically), also in logscripts.js
        * Config now comes from environment variable WEBVIEW_CONFIG
        * Load site_siteurl preferences from config section into config
          to allow multiple sites on a server.
        * Main.py now loads pythonpaths from config file
        * Main.py checks if weberror.errormiddleware exists else uses
          simpler error reporting function
    2015-2-20 Marc Berthoud, Various improvements
        * Update code for using astropy.io.fits
    2014-4-3 Marc Berthoud, Added self.infohead to model object to specify
        which header contains main information.
    2012-11-13 Marc Berthoud, Ability to specify instrument name and icons
        * Ability to have information come from specific headers
        * Configuration file name is now in main.py
    2012-9-13 Marc Berthoud, Added file name and format flexibility
        * Added flexible detection of pipe step in file name (model.filelist)
        * Added ability to have no image in primary FITS header
    2012-6-15 Marc Berthoud, Added use of jQuery for JavaScript elements
        * New ['scripts'] section in the configuration, scripts are now
          loaded in the page header
        * Updated logscripts.js for use of jQuery
    2012-4-12 Marc Berthoud, Various improvements during system testing
        * Validate flights and aors to make sure data is present
        * Add INSTMODE to the end of AOR entries in data
    2011-11-23 Marc Berthoud, Ver0.2: Added imageanalysis javascript object
        to the viewer to manage client side user interface.
    2011-1-31 Marc Berthoud, Ver0.1: Wrote and Tested
"""
