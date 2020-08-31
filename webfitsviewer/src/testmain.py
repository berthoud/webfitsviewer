#!/usr/bin/env python

""" Test program to see if the web server starts up correctly
    and the minimal python libraries are available
"""

import os,sys
import traceback
from wsgiref.handlers import CGIHandler

# Uncomment the following line to make sure configobj is available
#from configobj import ConfigObj

def app(environ, start_response):
    """ CGI application that returns errors
    """
    # Start document
    start_response('200 OK',[('Content-Type','text/html')])
    output = """<html><head><title>Web View Test Page</title></head><body>
<h1>Web Viewer Application Test Script</h1>
This page is intended as a basic check to see if your webserver is set up for WebFitsView.
The application will not run until all the checks below are successful.
"""
    ### Run Checks
    output += "<h2>Checks</h2>"
    try:
        # Check if WEBVIEW_CONFIG exists and points to valid file
        conffilename = None
        if not 'WEBVIEW_CONFIG' in environ:
            output += "<p>&#128721; Missing WEBVIEW_CONFIG environment Variable"
        elif not os.path.exists(environ['WEBVIEW_CONFIG']):
            output += "<p>&#128721; WEBVIEW_CONFIG = %s does not point to valid and visible file" % environ['WEBVIEW_CONFIG']
        else:
            conffilename = environ['WEBVIEW_CONFIG']
            output += "<p>&#10004; WEBVIEW_CONFIG = %s points to an existing file" % conffilename
        # Check if configobj can me imported
        try:
            from configobj import ConfigObj
            output += "<p>&#10004; ConfigObj package found"
        except:
            output += "<p>&#128721; Unable to import ConfigObj:"
            output += traceback.format_exc().replace('\n','<br>\n')
            conffilename = None
        # Check if config can be loaded
        if conffilename: 
            try:
                conf = ConfigObj(conffilename)
                output += "<p>&#10004; webview configuration file loaded"
            except:
                output += "<p>&#128721; Unable to load webview configuration file"
                conffilename = None
        # Check if [path] exists in config
        if conffilename:
            if 'path' in conf:
                output += "<p>&#10004; [path] section found in webview config"
            else:
                output += "<p>&#128721; No [path] section in webview config"
    except:
        output += "<p>&#128721; Some checks failed: <br>"
    ### Add diagnostic information
    diag = "<h2>Diagnostics</h2>"
    # Print python version
    diag += "<p><b>Python Version:</b><br> %s" % (sys.version)
    diag += "<br><b>Python Executable:</b><br> %s" % (sys.executable)
    # Print environment variables
    diag += "<p><b>Environment Variables:</b><br>"
    for v in environ:
        diag += v + " : " + repr(environ[v])+"<br>"
    output += diag
    output += "</body></html>"
    return [output.encode()]

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    CGIHandler().run(app)

