#!/usr/bin/env python

from wsgiref.handlers import CGIHandler

def app(environ, start_response):
    """ CGI application that returns errors
    """
    start_response('200 OK',[('Content-Type','text/html')])
    output = """<html><body>
<h1>WebFitsViewer Application Test Script</h1>
<b>Diag</b> = %s
</body>
</html>
"""
    diag = "Diagnosic data:<br>"
    for v in environ:
        diag += v + " : " + repr(environ[v])+"<br>"
    output = (output % repr(diag))
    return [output]

# Call main for the application to be callable as cgi script
if __name__ == '__main__':
    CGIHandler().run(app)


#print("Content-Type: text/html")
#print()
#print("<html><body>Testserver</body></html>")
#print()
#print()
