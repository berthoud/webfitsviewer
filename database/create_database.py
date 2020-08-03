import mysql.connector as mysql
from astropy.io import fits
import os 

# The below path is to a directory that holds ONLY fits files
# which will be added to the database as a test.
path_to_sample_data = 'data'
# The password should be set to whatever the password to the root account of your server is. 
# The default root password depends on your system.
root_password = "SEO"
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


# ---------------------------------------------------------------------------
# The below functions handle adding records to the table. They are currently only included for 
# testing and will be moved to the pipestep soon

def sql_field_to_hdu_field(sql_field):
    hdu_field = sql_field.upper().replace('_', '-')
    if hdu_field[-1] == '-':
        return hdu_field[:-1]
    else:
        return hdu_field

def hdu_field_to_sql_field(hdu_field):
    sql_field = hdu_field.lower().replace('-', '_')
    sql_keywords = {'DEC'}
    if sql_field in sql_keywords:
        return sql_field[:] + '_'
    else:
        return sql_field
    
"""
Extracts sql field values from hdu header values for each file in the given path and returns
a tuple that can be used to add them to the database. Assumes that 'file_path' is primary key
Arguments:
string path-path to diretory holding only FITS files we want added to database
RETURNS: 
return a tuple: (query, values), where query is of the form 
INSERT INTO fits_data (<comma delimited list of fields of fits_data>) VALUES (%s, %s, %s, ...)
(the number of %s is the same as the number of fields.)
and values, an array of tuples, where each tuple has the values corresponding to the 
fits_data fields, extracted from hdu headers of the fits files in path.
cursor.executemany(query, values) followed by db.commit() will insert the values into the database
"""
def get_add_records_cmd(path):
    sql_fields = [sql_field for (sql_field, _) in fields_and_types if sql_field]
    fields_str = ', '.join(sql_fields)
    format_specifiers = ', '.join(["%s"] * len(sql_fields))
    insert_query = f'INSERT INTO fits_data ({fields_str}) VALUES ({format_specifiers})'

    hdu_fields = [sql_field_to_hdu_field(sql_field) for sql_field in sql_fields if sql_field != 'file_path']
    header_vals = []
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        hdus = fits.open(full_path)
        # The below assumes that we will always have only one hdu per file
        # is that the case in practice?
        primary_hdu = hdus[0]
        curr_header_vals = [primary_hdu.header[hdu_field] for hdu_field in hdu_fields]
        # Add path to file to end of header vals
        curr_header_vals = [full_path] + curr_header_vals
        header_vals.append(tuple(curr_header_vals))
        hdus.close()
    return (insert_query, header_vals)


print('Before addition, rowcount is ', cursor.rowcount)
(query, values) = get_add_records_cmd(path_to_sample_data)
print(query, values)
cursor.executemany(query, values)
db.commit()
print('After addition, rowcount is ', cursor.rowcount)

cursor.close()
db.close()
