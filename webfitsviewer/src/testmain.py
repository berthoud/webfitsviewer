#!/usr/bin/env python

""" Test program to see if the web server runs correctly
    and the minimal python libraries are available
"""

import os,sys
from wsgiref.handlers import CGIHandler

# Uncomment the following line to make sure configobj is available
#from configobj import ConfigObj

def app(environ, start_response):
    """ CGI application that returns errors
    """
    # Start document
    start_response('200 OK',[('Content-Type','text/html')])
    output = """<html><body>
<h1>WebFitsViewer Application Test Script</h1>
This page is intended as a basic check to see if your webserver is set up for WebFitsView.
"""
    ### Run Checks
    output += "<h2>Checks</h2>"
    try:
        # See if WEBVIEW_CONFIG exists and points to valid file
        if not 'WEBVIEW_CONFIG' in environ:
            output += "<p>&#128721; Missing WEBVIEW_CONFIG environment Variable"
        elif not os.path.exists(environ['WEBVIEW_CONFIG']):
            output += "<p>&#128721; WEBVIEW_CONFIG = %s does not point to valid and visible file" % environ['WEBVIEW_CONFIG']
        else:
            output += "<p>&#10004; WEBVIEW_CONFIG = %s is valid" % environ['WEBVIEW_CONFIG']
        # Print python version
        output += "<p>&#10004; Python Version %s" % (sys.version)
    except:
        output += "<p>&#128721; Some checks failed"
    ### Add diagnostic information
    diag = "<h2>Diagnostics</h2> <b>Environment Variables:</b><br>"
    for v in environ:
        diag += v + " : " + repr(environ[v])+"<br>"
    output += diag
    output += "</body></html>"
    return [output]

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    CGIHandler().run(app)

