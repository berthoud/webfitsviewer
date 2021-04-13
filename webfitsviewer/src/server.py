""" Wrapper for the software that creates a webserver to serve the
    site locally. The wrapper uses wsgiref.simple_server.
"""

# Import
from controller import SiteController
from wsgiref.simple_server import make_server

# Set up application function
def app(environ, start_response):
    # Get the Path Info
    pathinfo = environ['PATH_INFO']
    # Check if webview folder is requested as expected  
    if not '/webviewserve' in pathinfo:
        start_response('200 OK', [('Content-Type', 'text/html')])
        output = '<h1>It Works!</h1>'
        return [output]
    # Check if it's a file
    filename = ''
    if '/webviewserve/static' in pathinfo:
        filename = pathinfo[10:]
    elif '/webviewserve/temp/images' in pathinfo:
        filename = pathinfo[10:]
    elif 'webviewserve/filedata' in pathinfo:
        filename = pathinfo[10:]
    # If it's a file, return it
    if len(filename) > 0:
        # Set File Name
        filename = '../'+filename
        print "Filename = %s" % filename
        # Get the Content Type
        if filename[-4] == '.css': ctype = 'text/css'
        else: ctype = 'text/html'
        # Start Request
        start_response('200 OK',[('Content-Type',ctype)])
        # Return File
        return [file(filename).read()]
    # Else run the script
    output = SiteController()(environ, start_response)
    return [output]


# Run the server
httpd = make_server('127.0.0.1',8042,app)
print "Serving http at 127.0.0.1 on port 8042"
#httpd.handle_request()
httpd.serve_forever()
