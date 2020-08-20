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
passed in. Change them as needed for the program to run. 
"""
default_sql_user = 'root'
default_sql_pass = 'SEO'
default_db_config_path = './database_config.txt'
overwrite = False

parser = argparse.ArgumentParser(description='Create a basic FITS database')
parser.add_argument('-user', '--user', 
    default=default_sql_user, help='SQL user to use')
parser.add_argument('-pass', '--pass', 
    default=default_sql_pass, 
    help='SQL user password to use. \
        Optionally can be path to file contianing only the sql_pass.')
parser.add_argument('-configpath', '--configpath', 
    default=default_db_config_path, help='db config path')
parser.add_argument('-overwrite', '--overwrite', action='store_true',
    help='Whether to overwrite already existing table or not. Boolean')
dict_args = vars(parser.parse_args())

sql_user = dict_args['user']
sql_pass = dict_args['pass']
# Treat pass as a file holding the pass on the first line if possible
if os.path.exists(sql_pass):
    print('Using sql pass found in file: ', sql_pass)
    with open(sql_pass, 'r') as pass_file:
        # Get rid of accidental new lines
        sql_pass = pass_file.readline().replace('\n', '')
path_to_config = dict_args['configpath']    
overwrite = dict_args['overwrite']

# The below code connects to the database. To do this, you must have your local sql server running.
# (In practice we will make other mysql users which can be done easily from the command line as needed
# and not access from the root).

db = mysql.connect(
    host="localhost",
    user=sql_user,
    passwd=sql_pass,
    auth_plugin='mysql_native_password'
)

cursor = db.cursor()

# Create the seo database if it does not exist
cursor.execute("CREATE DATABASE IF NOT EXISTS seo")
cursor.execute("USE seo;")

def create_table(cursor, table_name, table_dict, pk_key='primary_key', overwrite=True):
    """
    Within the SEO database, creates a table table_name using a table_dict of the format
    obtained by parsing the database config. Note that db.commit() is not called so if 
    autocommit is not true for the cursor you will have to call it to finalize creation

    Parameters:
    cursor: the mysql-connector-python cursor to an open database.

    table_name: the name of the table to be craeted

    table_dict: a dict of the format obtained by parsing the database config describing
    the table to be created. Every key should be the name of a desired sql_field, and its
    corresponding value should be the type of the field. There should also be one more 
    key named 'primary_key' whose value is the sql_field to be used as a primary key.
    Will throw runtime error if table_dict does not have at least 2 keys including 
    primary_key.

    pk_key: the name of the key that specifies the primary_key of the SQL table

    overwrite: If True, the function will DROP the old table
    before continuing. Otherwise it will not overwrite it

    Returns:
    Returns None.
    Creates a new table with table_name populated using table_dict.
    Throws RuntimeError under following conditions
    -config_dict lacks 'primary_key' key
    -config_dict has < 2 keys including 'primary_key'
    -config_dict maps to invalid SQL types
    -SEO database has not yet been created
    """
     # pk_key is the key in a table dict storing the name of its primary key
    if pk_key not in table_dict:
        raise RuntimeError(f'Config for {table_name} lacks required key {pk_key}!')
    elif len(table_dict) < 2:
        err_msg = f'Config for {table_name} has {len(table_dict)} entries; at least 2 required.'
        raise RuntimeError(err_msg)
    
    try:
        cursor.execute('USE seo;')
    except mysql.errors.ProgrammingError as err:
        new_err_msg = "The above error could mean the SEO database hasn't been created yet!"
        raise RuntimeError(new_err_msg) from err

    create_table_cmd = []

    if overwrite:
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        create_table_cmd.append(f'CREATE TABLE {table_name} (')
    else:
        create_table_cmd.append(f'CREATE TABLE IF NOT EXISTS {table_name} (')
    
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
    create_table(cursor, table_name, tables[table_name], pk_key, overwrite)
    db.commit()
    print(f'Columns of table {table_name} parsed from config file: ')
    cursor.execute("DESC fits_data;")
    print(cursor.fetchall(), '\n')

# Current testing assumes fits_data table
if not 'fits_data' in tables:
    print('Skipping insertion of phon test data because fits_data table used in testing DNE')
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