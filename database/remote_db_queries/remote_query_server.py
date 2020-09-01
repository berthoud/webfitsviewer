from wsgiref.simple_server import make_server
from wsgiref.handlers import CGIHandler
import mysql.connector as mysql
import json
from decimal import Decimal


def exec_db_query(query):
    # When the server is open to foreign requests, make sure that the user used
    # can only make select commands for the fits_data table. 
    sql_user = 'root'
    sql_pass = 'SEO'
    db = mysql.connect(
        host='127.0.0.1',
        user=sql_user,
        passwd=sql_pass,
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor()
    cursor.execute('USE seo;')
    cursor.execute(query)
    print(query)
    query_result = cursor.fetchall()
    cursor.close()
    db.close()

    return query_result


def application(environ, start_response):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    
    if request_body_size > 0:
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)['query']
        #cols = data['cols']
        #col_format_specifiers = ('%s, ' * len(cols))[:-2]
        #where = data['where']

        #query = 'SELECT '
        query_result = exec_db_query(data)
        # Some SQL_fields are the decimal type which can't be parsed into JSON.
        # The below changes these fields to be floats.
        for (i, tup) in enumerate(query_result):
            query_result[i] = list(tup)
            for j in range(len(query_result[0])):
                if isinstance(query_result[i][j], Decimal):
                    query_result[i][j] = float(query_result[i][j])
        print('Got the following query result to a request: ', query_result)
        response_body = json.dumps(query_result)
    else:
        response_body = 'No query made'

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    response = [response_body.encode('utf-8')]
    return response

run_as_cgi = 1
if run_as_cgi:
    if __name__ == '__main__':
        CGIHandler().run(application)
else:
    with make_server('localhost', 8051, application) as httpd:
        print('Serving application on port 8051...')
        httpd.serve_forever()
