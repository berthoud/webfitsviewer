#!/usr/bin/env python

""" Main function to be used as CGI script or to create WSGI application.

    To get the correct config file: use the following in the server .conf
        SetEnv WEBVIEW_CONFIG "/path/to/webview_config.txt"
    To get the correct python version: set the PATH in the server .conf
        SetEnv PATH "/opt/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

"""

# Imports
import sys
import os
from configobj import ConfigObj # Configuration Object
# Load configuration
conf = ConfigObj(os.environ['WEBVIEW_CONFIG'])
# Add to pythonpath (get from config)
if 'pythonpath' in conf['path']:
    newpaths = conf['path']['pythonpath'].split('\n')
    newpaths = [p.strip() for p in newpaths]
    for np in newpaths:
        if np not in sys.path:
            sys.path.append(np)

# Import - check if possible to import weberror.errormiddleware
import traceback
from wsgiref.handlers import CGIHandler
weberror_imported = False # flag to indicate with error wrapper to use
try:
    from weberror.errormiddleware import ErrorMiddleware # @UnresolvedImport
    weberror_imported = True
except:
    pass

# Define Application
def app(environ, start_response):
    """ Application for WSGI operation. The application creates a
        SiteController object and calls it. The SiteController is expected
        to call start_response. The ouput from SiteController is returned.
    """
    from controller import SiteController # has to be in here to catch errors
    controller = SiteController()
    output = controller(environ,start_response)
    return [output.encode()]

# Define Application with error handler
#application = ErrorMiddleware(app, debug = True,
#                              error_message = 'HAWC Viewer Error')

# Define application that returns errors
def errapp(environ, start_response):
    """ CGI application that returns errors
    """
    try:
        from controller import SiteController
        #environ['wsgi.input']=''
        controller = SiteController()
        output = controller(environ,start_response)
    except Exception, e:
        start_response('200 OK',[('Content-Type','text/html')])
        output = """<html><body>
<b>Error</b> = %s<br>
%s<p>
<b>Path</b> = %s<p>
<b>Diag</b> = %s
</body>
</html>
"""
        diag = "Diagnosic data:<br>\n"
        for v in environ:
            diag += v + " : " + repr(environ[v])+"<br>\n"
        output = output % (repr(e), traceback.format_exc().replace('\n','<br>\n'),
                           repr(sys.path), diag)
    return [output.encode()]

# Define WSGI application
if weberror_imported:
    application = ErrorMiddleware(app, debug = True,
                                  error_message = 'HAWC Viewer Error')
else:
    application = errapp

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    CGIHandler().run(application)
    
