import mysql.connector as mysql
from astropy.io import fits
import os 
import sys
import argparse

"""
Creates a basic SQL database based on a database config that follows the format 
described in the readme. Assumes you have a local SQL server running. For command line
arguments description type create_database.py -h

More specifically, will create an "seo" database and within that a fits_data table.
Fills it with phony records for testing purposes.

The next few lines store default values for the command line parameters if they are not
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
# For testing purposes, you may want to comment out the above and uncomment out the below
# to make the database anew. Obviously don't do this on the actual database
#cursor.execute("DROP DATABASE seo")
#cursor.execute("CREATE DATABASE seo")

cursor.execute("SHOW DATABASES")
# Make sure 'seo' has been created
assert ('seo',) in cursor.fetchall()

# Make future commands be within the seo database
cursor.execute("USE seo;")

def parse_config(path_to_config):
    """
    Parses given config file and returns the parsed SQL table fields and types. Does not
    check for correctness of fields and types.

    Parameters:
    path_to_config: Config file for fits_data table. Every line must be blank,
    start with #, or be of the format "<field name> <whitespace> <field_type (optional)>
    
    Returns:
    Returns a list of tuples of strings where each tuple is of the form 
    (parsed_field_name, parsed_field_type). If a field type is left out, 'varchar(15)' is used.
    Note that field names and types have not been checked for whether they are valid in SQL. 
    """
    sql_fields_and_types = []
    with open(path_to_config, 'r') as config:
        for line in config:
            trimmed = line.strip()
            # If line is a comment or only whitespace keep going
            if trimmed.startswith("#") or len(trimmed) == 0:
                continue
            field_and_type = trimmed.split(maxsplit=1)
            DEFAULT_TYPE = 'varchar(15)'
            if len(field_and_type) == 1:
                field_and_type.append(DEFAULT_TYPE)
            sql_fields_and_types.append(tuple(field_and_type))
    return sql_fields_and_types

def create_fits_data_table(cursor, path_to_config, overwrite):
    """
    Within the SEO database, createst a fits_data table 
    and populates it with fields in the config file parsed using parse_config. 
    Deletes the fits_data table if it does not yet exist.

    Parameters:
    cursor: the mysql-connector-python cursor to an open database.
    path_to_config: the path to the config file containing fields for the new table.

    overwrite: If True, then a call to create_fits_data_table will DROP the old fits_data
    table before continuing. If False and an old fits_data table exists, the function will
    not overwrite it and the returned fields_and_types list will be what is in the config
    file whether that is recent or not.

    Returns:
    Returns the fields_and_types list of tuples from parse_config. 
    Populates new table with fields from config file.
    Note that if overwrite is False and config file is not up to date the returned
    fields and types will be out of date
    Throws RuntimeError under following conditions
    -Config file is empty
    -Config file has malformed entries
    -SEO database has not yet been created
    """
    fields_and_types = parse_config(path_to_config)
    if len(fields_and_types) == 0:
        raise RuntimeError('Config file is empty!')

    try:
        cursor.execute('USE seo;')
    except mysql.errors.ProgrammingError as err:
        new_err_msg = "The above error could mean the SEO database hasn't been created yet!"
        raise RuntimeError(new_err_msg) from err

    create_table_cmd = []

    if overwrite:
        cursor.execute('DROP TABLE IF EXISTS fits_data;')
        create_table_cmd.append('CREATE TABLE fits_data (')
    else:
        create_table_cmd.append('CREATE TABLE IF NOT EXISTS fits_data (')

    for (field, sql_type) in fields_and_types:
        create_table_cmd.append(f'{field} {sql_type},')
    # First entry in config is primary key
    create_table_cmd.append(f'PRIMARY KEY ({fields_and_types[0][0]})')
    create_table_cmd.append(');')
    create_table_cmd = ' '.join(create_table_cmd)
    try:
        cursor.execute(create_table_cmd)
    except mysql.errors.ProgrammingError as err:
        new_err_msg = 'The above error may indicate malformed config file'
        raise RuntimeError(new_err_msg) from err
    return fields_and_types

fields_and_types = create_fits_data_table(cursor, path_to_config, overwrite)
# The above created a table called "fits_data"
print('\nColumns of table parsed from config file: ')
cursor.execute("DESC fits_data;")
print(cursor.fetchall(), '\n')

def add_phony_data(fields_and_types, field_values, cursor):
    """
    Takes a list of tuples storing the SQL databases fields and their types
    as returned by creates_fits_data, the values for the fields within that,
    and a database cursor, and attempts to add the field values to the database
    db.commit() must be called for changes to take effect

    Parameters:
    fields_and_types: A list of tuples storing the SQL database fields and their types
    as returned by create_fits_data. 
    field_values: A list of values whose types match the types of fields_and_types. 
    Order matters. 
    cursor: the database cursor used to execute the insertion of data.

    Returns: None. Will throw mysql.errors.ProgrammingError if the query or cursor is invalid
    
    """
    sql_fields = [sql_field for (sql_field, _) in fields_and_types]
    fields_str = ', '.join(sql_fields)
    format_specifiers = ', '.join(["%s"] * len(sql_fields))
    insert_query = f'INSERT INTO fits_data ({fields_str}) VALUES ({format_specifiers})'
    try:
        cursor.execute(insert_query, field_values)
    except mysql.errors.IntegrityError as err:
        err_msg = ('This error likely means the phony record added has the same file path '
            'as another record in the fits_data table. One way to fix this is to set '
            'the -overwrite flag to True when calling create_database. Note that this will '
            'not just overwrite the duplicate records but the entire fits_data table')
        raise RuntimeError(err_msg) from err
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
add_phony_data(fields_and_types, field_values, cursor)
db.commit()
print('After addition, rowcount is ', cursor.rowcount)
print('Table looks like this')
cursor.execute('SELECT * FROM fits_data;')
print(cursor.fetchall())

cursor.close()
db.close()
