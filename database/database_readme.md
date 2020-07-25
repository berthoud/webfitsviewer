This is the initial database code. To run, you need to 
1) have mysql installed and the server running
2) have the requirements listed in requirements.txt. You should be able to get these by just installing astropy and mysql-connector-pytthon. Make sure you don't accidentally install mysql-connector; the command should be "pip install mysql-connector-python". You may [run into there error described here](https://stackoverflow.com/questions/50557234/authentication-plugin-caching-sha2-password-is-not-supported) if you don't do this. (If you get that error despite having the right thing installed, try uninstalling and installing again; it worked for me.)
3) Go into create_database.py and edit the two paths at the top and the root password. You may need to google around to figure out what the default root password is for your mysql sever. Note that the path_to_sample_data should be a directory that holds some FITS files and no files that are not FITS files. 

If you do all of the above, you should be able to run create_databases.py and it will 
1) create an seo database within your mysql server
2) create a fits_data table within that database, with fields described in fits_data_table_config.py
3) populate that seo table using the FITS files in path_to_sample_data. 
Note that repeated reruns will delete and recreate the table. I recommend reading the code and comments as alternatives are commented out sometimes, in particular with regards to deleting already existing things.

TESTING: With regards to seeing the results from the code, I recommend just running mysql in the command line. After successfully running create_database.py, you can run the following sequence of commands to understand what occurred:
mysql -u root -p <will prompt you for root password>
SHOW DATABASES <shows databases, should include the seo one the code creates>
USE seo 
SHOW TABLES <shows tables within seo, should include fits_data one created by code>
DESC fits_data <should show fields of fits_data table>
SELECT * FROM fits_data <should show records added from your path_to_data>

Feel free to reach out if you run into problems.
