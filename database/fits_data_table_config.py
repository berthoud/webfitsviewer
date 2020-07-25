from astropy.io import fits
import os 

"""
My thinking on field naming convention: fits headers use hyphens to delimit 
abbreviations of words, as in DATE-OBS, and are all caps. SQL fields cannot contain hyphens,
so I suggest we replace them with underscores, and they are by convention in lowercase.
When processing, you could just do str.replace('-', '_') and str.upper()
Another problem is that same HDU fields such as dec are sql keywords. For these I suggest
we add a trailing underscore that we can check for and remove when processing.
Another alternative is to define a dictionary mapping SQL fields to HDU fields.
"""
# Note that the below list does not include the file_path field
fields_and_types = [
    ('date_obs', 'varchar(19)'),
    ('simple_', 'varchar(1)'),
    ('bitpix', 'TINYINT'),
    ('ra', 'varchar(11)'),
    ('dec_', 'varchar(12)'),
    ('exptime', 'decimal(5, 2)')
]

def create_table(cursor):
    cursor.execute('USE seo;')
    #create_cmd = 'CREATE TABLE IF NOT EXISTS fits_data (file_path varchar(255) NOT NULL, PRIMARY KEY (file_path));'
    #cursor.execute(create_cmd)
    # The lines above will not remake the table if it exists, leading to an error. 
    # Current functionality will always remake the table.
    cursor.execute('DROP TABLE IF EXISTS fits_data;')
    cursor.execute('CREATE TABLE fits_data (file_path varchar(255) NOT NULL, PRIMARY KEY (file_path));')
    alter_table_cmd = []
    alter_table_cmd.append('ALTER TABLE fits_data')
    for (i, (field, type)) in enumerate(fields_and_types):
        end = ';' if i == (len(fields_and_types) - 1) else ','
        alter_table_cmd.append(f'ADD {field} {type}' + end)
    str_alter_cmd = ' '.join(alter_table_cmd)
    cursor.execute(str_alter_cmd)

def sql_field_to_hdu_field(sql_field):
    hdu_field = sql_field.upper().replace('_', '-')
    if hdu_field[-1] == '-':
        return hdu_field[:-1]
    else:
        return hdu_field

def hdu_field_to_sql_field(hdu_field):
    sql_field = hdu_field.lower().replace('-', '_')
    sql_keywords = {'SIMPLE', 'DEC'}
    if sql_field in sql_keywords:
        return sql_field[:] + '_'
    else:
        return sql_field
    
"""
Extracts sql field values from hdu header values for each file in the given path and returns
a tuple that can be used to add them to the database.
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
    sql_fields = [sql_field for (sql_field, _) in fields_and_types]
    # Add file_path field to sql_fields list's back
    sql_fields.append('file_path')
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
        curr_header_vals.append(full_path)
        header_vals.append(tuple(curr_header_vals))
        hdus.close()
    return (insert_query, header_vals)



