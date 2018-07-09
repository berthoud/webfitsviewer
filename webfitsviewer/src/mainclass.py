#!/usr/local/bin/python

'''#!/usr/bin/env python
'''

""" Main function to be used as CGI script or to create WSGI application.
    This version of the program contains 
"""

# Global Variables
Config_FilePathName = '../config/webviewclass_config.txt'

# Add site packages to path
import sys
import os
newpaths = ['/data/scripts/DataReduction/source',
            '/data/scripts/fitsview/src',
            '/data/scripts/fitsview/libs/weberror-master',
            '/data/scripts/fitsview/libs/Paste-2.0.3']
for np in newpaths:
    if np not in sys.path:
        sys.path.append(np)

#print(sys.path)

# Import
from wsgiref.handlers import CGIHandler
#from weberror.errormiddleware import ErrorMiddleware # @UnresolvedImport
import traceback

# Define Application
def app(environ, start_response):
    """ Application for WSGI operation. The application creates a
        SiteController object and calls it. The SiteController is expected
        to call start_response. The ouput from SiteController is returned.
    """
    from controller import SiteController
    controller = SiteController(config_filepathname = Config_FilePathName)
    output = controller(environ,start_response)
    return [output]

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
        controller = SiteController(config_filepathname = Config_FilePathName)
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
    return [output]

# Define a start response for non-cgi stuff
def startresp(a,b):
    print('Status: 200 OK')
    print('Content-Type: text/html')
    print('')
    print('')
    
# A function that just runs the whole thing and returns errors 
def errrun():
    """ WSGI application, this version catches and return errors with 
        ok status (in case your webserver catches the info you want to see)
    """
    try:
        from controller import SiteController
        controller = SiteController(config_filepathname = Config_FilePathName)
        output = controller(os.environ,startresp)
        print(output)
    except Exception, e:
        print('Status: 200 OK')
        print('Content-Type: text/html')
        print('')
        print('')
        output = """<html><body>
Error found = %s<p>
%s<p>
Path = %s
Diag = %s
</body>
</html>
"""
        diag = "Diagnosic data:<br>\n"
        for v in os.environ:
            diag += v + " : " + repr(os.environ[v])+"<br>\n"
        output = output % (repr(e), traceback.format_exc().replace('\n','<br>\n'),
                           repr(sys.path), diag)
        print(output)

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    # One of the following lines has to be commented out
    # CGIHandler().run(application) # Run CGI application with weberror
    # CGIHandler().run(app) # Run CGI application only
    CGIHandler().run(errapp) # Run CGI application with simple error handlin
    # errrun() # Run appliation with error hanling without CGI
