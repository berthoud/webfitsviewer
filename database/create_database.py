import mysql.connector as mysql
from astropy.io import fits
import os 
import sys

# The below path is to a directory that holds ONLY fits files
# which will be added to the database as a test.
path_to_sample_data = 'data'
# The password should be set to whatever the password to the root account of your server is. 
# The default root password depends on your system.
root_password = "SEO"
# Optionally pass in the root password as command line argument
if len(sys.argv) > 1:
    root_password = sys.argv[1] 
# Next is the path_to_confi which you shouldn't need to change as it comes from github.
path_to_config = "./database_config.txt"


# The below code connects to the database. To do this, you must have your local sql server running.
# (In practice we will make other mysql users which can be done easily from the command line as needed
# and not access from the root).

db = mysql.connect(
    host="localhost",
    user="root",
    passwd=root_password,
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

def create_fits_data_table(cursor, path_to_config, overwrite=True):
    """
    Within the SEO database, createst a fits_data table 
    and populates it with fields in the config file parsed using parse_config. 
    Deletes the fits_data table if it does not yet exist.

    Parameters:
    cursor: the mysql-connector-python cursor to an open database.
    path_to_config: the path to the config file containing fields for the new table.

    overwrite: If True, then a call to create_fits_data_table will DROP the old fits_data
    table before continuing. If False and an old fits_data table exists, then the function
    will throw an error and stop. 

    Returns:
    Returns the fields_and_types list of tuples from parse_config. 
    Populates new table with fields from config file.
    Throws RuntimeError under following conditions
    -Config file is empty
    -Config file has malformed entries
    -SEO database has not yet been created
    -fits_data table has been created already and overwrite=False 
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
        # Will throw error if table already exists
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
        new_err_msg = 'The above error may indicate malformed config file ' \
                      + 'or that overwrite=False and fits_data already exists'
        raise RuntimeError(new_err_msg) from err
    return fields_and_types

fields_and_types = create_fits_data_table(cursor, path_to_config)
# The above created a table called "fits_data"
cursor.execute("DESC fits_data;")
print(cursor.fetchall())

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
    cursor.execute(insert_query, field_values)

print('Before addition, rowcount is ', cursor.rowcount)
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

cursor.close()
db.close()
