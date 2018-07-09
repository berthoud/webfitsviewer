#!/opt/miniconda/bin/python

#!/usr/bin/env python

""" Main function to be used as CGI script or to create WSGI application.
"""

# Global Variables
Config_FilePathName = '../config/webview2017B_config.txt'

# Add site packages to path
import sys
newpaths = ['/data/hawc/Pipeline/hawcdrp/pipeline/src']
for np in newpaths:
    if np not in sys.path:
        sys.path.append(np)

# Import
from controller import SiteController
from wsgiref.handlers import CGIHandler
from weberror.errormiddleware import ErrorMiddleware # @UnresolvedImport

# Define Application
def app(environ, start_response):
    """ Application for WSGI operation. The application creates a
        SiteController object and calls it. The SiteController is expected
        to call start_response. The ouput from SiteController is returned.
    """
    controller = SiteController(config_filepathname = Config_FilePathName)
    output = controller(environ,start_response)
    return [output]


# Define Application with error handler
application = ErrorMiddleware(app, debug = True,
                              error_message = 'HAWC Viewer Error')

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    CGIHandler().run(application)
