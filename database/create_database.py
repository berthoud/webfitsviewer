import mysql.connector as mysql
import configobj
import os 
from sys import exit
import argparse

"""
Creates a basic SQL database named 'SEO' based on a database config that follows the format 
described in the readme. Assumes you have a local SQL server running. For command line
arguments description type create_database.py -h
Fills it with phony records for testing purposes.

The first few lines store default values for the command line parameters if they are not
passed in. Change them as needed for the program to run. The defaults for the boolean 
parameters cannot be changed.
"""
default_sql_user = 'root'
default_sql_pass = 'SEO'
default_db_config_path = './database_config.txt'
default_db_name = 'SEO'

parser = argparse.ArgumentParser(description='Create a basic FITS database')
parser.add_argument('-user', '--user', 
    default=default_sql_user, help='SQL user to create database from')
parser.add_argument('-pass', '--pass', 
    default=default_sql_pass, 
    help='SQL user password to use. \
        Optionally can be path to file containing only the sql_pass.')
parser.add_argument('-configpath', '--configpath', 
    default=default_db_config_path, help='path to database config')
parser.add_argument('-overwrite', '--overwrite', action='store_true',
    help='Whether to overwrite already existing table or not. Boolean')
parser.add_argument('-add_phony', '--add_phony', action='store_true',
    help=('Whether to try to add hardcoded phony data to the database. ' 
    'Assumes config is consistent with the hardcoded values. Boolean.'))
parser.add_argument('-dbname', '--dbname', 
    default=default_db_name, 
    help='The name of the database to create that will store the tables described in the config')
parser.add_argument('-create_users', '--create_users', action='store_true',
    help=('Whether to create the users described in the config.'
        'Must be manually deleted so be wary.'))
parser.add_argument('-overwrite_users', '--overwrite_users', action='store_true',
    help='Whether to overwrite exiting users. Only has effect used with -create_users')
dict_args = vars(parser.parse_args())

sql_user = dict_args['user']
sql_pass = dict_args['pass']
# Treat pass as a file holding the pass on the first line if possible
if os.path.exists(sql_pass):
    print('Using sql pass found in first line of file: ', sql_pass)
    with open(sql_pass, 'r') as pass_file:
        # Get rid of accidental new lines
        sql_pass = pass_file.readline().replace('\n', '')
path_to_config = dict_args['configpath']    
db_name = dict_args['dbname']
overwrite = dict_args['overwrite']
add_phony = dict_args['add_phony']
create_users = dict_args['create_users']
overwrite_users = dict_args['overwrite_users']


try:
    db = mysql.connect(
        host="localhost",
        user=sql_user,
        passwd=sql_pass,
        auth_plugin='mysql_native_password'
    )
except mysql.errors.DatabaseError as err:
    err_msg = ('The raised exception could mean that the SQL server you are trying to '
        'connect to is not running.')
    raise RuntimeError(err_msg) from err
cursor = db.cursor()

# Create the seo database if it does not exist
cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name}')
cursor.execute(f'USE {db_name};')

def create_table(cursor, table_name, table_dict, db_name,
                 pk_key='primary_key', overwrite=True):
    """
    Within the specified database, creates a table table_name using a table_dict of the format
    obtained by parsing the database config. Note that db.commit() is not called so if 
    autocommit is not true for the cursor you will have to call it to finalize creation

    Parameters:
    cursor: the mysql-connector-python cursor to an open database.

    table_name: the name of the table to be craeted

    table_dict: If the database config was parsed using configobj as conf, then table_dict
    is of the form of conf['tables'][<table_name>]. In particular:
    Every key should be the name of a desired sql_field, and its
    corresponding value should be the type of the field. There should also be one more 
    key, the name of which is passed in as pk_key, whose value is the sql_field to be 
    used as a primary key. Will throw runtime error if table_dict does not have at least 
    2 keys including pk_key.

    db_name: The name of the database to add the table to.

    pk_key: the name of the key that specifies the primary_key of the SQL table

    overwrite: If True, the function will DROP the old table
    before continuing. Otherwise it will not change the existing table at all. This will 
    be printed to the user.

    Returns:
    Returns None.
    Creates a new table with table_name populated using table_dict.
    Throws RuntimeError under following conditions
    -config_dict lacks 'primary_key' key
    -config_dict has < 2 keys including 'primary_key'
    -config_dict maps to invalid SQL types
    -db_name database has not yet been created
    """
     # pk_key is the key in a table dict storing the name of its primary key
    if pk_key not in table_dict:
        raise RuntimeError(f'Config for {table_name} lacks required key {pk_key}!')
    elif len(table_dict) < 2:
        err_msg = f'Config for {table_name} has {len(table_dict)} entries; at least 2 required.'
        raise RuntimeError(err_msg)
    
    try:
        cursor.execute(f'USE {db_name};')
    except mysql.errors.ProgrammingError as err:
        new_err_msg = f"The above error could mean database {db_name} hasn't been created yet!"
        raise RuntimeError(new_err_msg) from err

    create_table_cmd = []

    if overwrite:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        create_table_cmd.append(f'CREATE TABLE {table_name} (')
    else:
        cursor.execute(
            f'SELECT * FROM information_schema.tables WHERE table_name="{table_name}";'
        )
        cursor.fetchone()
        if cursor.rowcount > 0:
            print(f'Overwrite is False and table "{table_name}" exists. \
            It will not be changed')
            return None
        create_table_cmd.append(f'CREATE TABLE {table_name} (')

    
    for (sql_field, sql_type) in table_dict.items():
        if sql_field == pk_key:
            continue
        create_table_cmd.append(f'{sql_field} {sql_type},')
    
    create_table_cmd.append(f'PRIMARY KEY ({table_dict[pk_key]})')
    create_table_cmd.append(');')
    create_table_cmd = ' '.join(create_table_cmd)
    try:
        cursor.execute(create_table_cmd)
    except mysql.errors.ProgrammingError as err:
        new_err_msg = 'The above error may indicate incorrect sql types in config!'
        raise RuntimeError(new_err_msg) from err

pk_key = 'primary_key'
config = configobj.ConfigObj(path_to_config, list_values=False, file_error=True)
tables = config['tables']
for table_name in tables:
    try:
        create_table(cursor, table_name, tables[table_name], db_name, pk_key, overwrite)
    except err:
        cursor.close()
        db.close()
        raise err
    db.commit()
    print(f'Columns of table {table_name} parsed from config file: ')
    cursor.execute("DESC fits_data;")
    print(cursor.fetchall(), '\n')

if create_users:
    users = config['users']
    for (_, user_data) in users.items():
        new_user = user_data['username']
        new_user_pass = user_data['pass']
        # Treat pass as a file holding the pass on the first line if possible
        if os.path.exists(new_user_pass):
            with open(new_user_pass, 'r') as pass_file:
                # Get rid of accidental new lines
                new_user_pass = pass_file.readline().replace('\n', '')

        host = user_data['host']
        if overwrite_users: # Drop user if it exists
            cursor.execute(f'SELECT User FROM mysql.user WHERE User="{new_user}";')
            cursor.fetchall()
            user_exists = cursor.rowcount > 0
            if user_exists:
                cursor.execute(f'DROP USER "{new_user}"@"{host}";')
        try:
            cursor.execute( 
                f'CREATE USER "{new_user}"@"{host}" IDENTIFIED BY "{new_user_pass}";'
            )
        except mysql.errors.DatabaseError as err:
            cursor.close()
            db.close()
            err_msg = ('This error could be caused by attempting to recreate an exiting user ' 
                'without using -overwrite_users')
            raise RuntimeError(err_msg) from err
        permissions = []
        if user_data.get('SELECT', 'False').lower() == 'true':
            permissions.append('SELECT')
        elif user_data.get('INSERT', 'False').lower() == 'true':
            permissions.append('INSERT')
        if permissions:
            str_permissions = ', '.join(permissions)
            cursor.execute(
                f'GRANT {str_permissions} ON {db_name}.* TO "{new_user}"@"{host}";'
            )
            cursor.execute('FLUSH PRIVILEGES;')
    db.commit()

if not add_phony:
    print('Exiting without attempting to add phony data because "-add_phony" not specified')
    exit()

# Current testing assumes fits_data table
if not 'fits_data' in tables:
    print(
        "Skipping insertion of phony test data because fits_data table used in testing \
            doesn't exist. If you like, you can change the coded in table name to \
            something else and the code may run.")
    exit()

print(('About to test insertion of phony data. This assumes that config file has not been '
    'edited from what is on GitHub. If it has been, edit the variable \'field_values\' '
    'in this file'))
print('Before addition of phony data, fits_data table looks like this:')
cursor.execute('SELECT * FROM fits_data;')
print(cursor.fetchall())
print('rowcount is', cursor.rowcount)
field_values = [
    'test_path',
    'T',
    'date_obs_val',
    5,
    'ra val',
    'dec val',
    123
]
sql_fields = [sql_field for sql_field in tables['fits_data'] if sql_field != pk_key]
fields_str = ', '.join(sql_fields)
format_specifiers = ', '.join(["%s"] * len(sql_fields))
insert_query = f'INSERT INTO fits_data ({fields_str}) VALUES ({format_specifiers})'
try:
    cursor.execute(insert_query, field_values)
except mysql.errors.IntegrityError as err:
    cursor.close()
    db.close()
    err_msg = ('This error likely means the phony record added has the same primary key '
        'as another record in the fits_data table. One way to fix this is to set '
        'the -overwrite flag to True when calling create_database. Note that this will '
        'not just overwrite the duplicate records but the entire fits_data table')
    raise RuntimeError(err_msg) from err

db.commit()
print('After addition, rowcount is ', cursor.rowcount)
print('Table looks like this')
cursor.execute('SELECT * FROM fits_data;')
print(cursor.fetchall())

cursor.close()
db.close()