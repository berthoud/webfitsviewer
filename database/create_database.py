import mysql.connector as mysql
import fits_data_table_config 

# The below is the path to the .sql file creating the fits_data table in 
# the seo database. This can be altererd to add new fields to the table
path_to_table_setup = "fits_data_table_config.sql"
# The below path is to a directory that holds ONLY fits files
# which will be added to the database as a test.
path_to_sample_data = 'data'
# The password should be set to whatever the password to the root account of your server is. 
# The default root password depends on your system.
root_password = "SEO"

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

cursor.execute("CREATE DATABASE IF NOT EXISTS seo")
# For testing purposes, you may want to comment out the above and uncomment out the below
# to make the database anew.
#cursor.execute("DROP DATABASE seo")
#cursor.execute("CREATE DATABASE seo")

cursor.execute("SHOW DATABASES")
# Make sure 'seo' has been created
assert ('seo',) in cursor.fetchall()

cursor.execute("USE seo;")

fits_data_table_config.create_table(cursor)

# The above created a table called "fits_data"
cursor.execute("DESC fits_data;")
print(cursor.fetchall())


print('Before addition, rowcount is ', cursor.rowcount)
(query, values) = fits_data_table_config.get_add_records_cmd(path_to_sample_data)
cursor.executemany(query, values)
db.commit()
print('After addition, rowcount is ', cursor.rowcount)
