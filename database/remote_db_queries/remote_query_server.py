#!/usr/bin/env python

from wsgiref.simple_server import make_server
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
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    data = json.loads(request_body)['query']
    query_result = exec_db_query(data)
    # Some SQL_fields are the decimal type which can't be parsed into JSON.
    # The below changes these fields to be floats.
    for (i, tup) in enumerate(query_result):
        query_result[i] = list(tup)
        for j in range(len(query_result[0])):
            if isinstance(query_result[i][j], Decimal):
                query_result[i][j] = float(query_result[i][j])
    print(query_result)

    status = '200 OK'
    response_body = json.dumps(query_result)
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body.encode('utf-8')]

httpd = make_server('localhost', 8051, application)
httpd.serve_forever()