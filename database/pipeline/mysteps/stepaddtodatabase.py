#!/usr/bin/env python
""" STEP AddToDatabase- Version 1.0.0

    This step registers an image with the local image database.

    It does this by parsing the database configuration file, which's path is given in the 
    step config file, for the desired fields from FITS HDUs. It then gets field values for those 
    fields from self.datain and executes an SQL statement adding the record. 
    As of now, even though the config specifies multiple tables, only the fits_data table
    is used

    Assumptions necessary for the step to run without error:
    -the 'SEO' database and 'fits_data' table within it must both have been created 
    -the database config file, the path of which is in the step config, must exist and not be empty
    -all database fields in the config file aside from the optional 'file_path' map to 
    FITS HDU fields by the sql_field_to_hdu_field function below (will be true if they 
    follow the convention in the config)
    
    @author: Enrique Collin
"""

import logging 
from darepype.drp import StepParent
import mysql.connector as mysql
from os import path
import configobj


class StepAddToDatabase(StepParent):
    """ HAWC Pipeline Step Parent Object
        The object is callable. It requires a valid configuration input
        (file or object) when it runs.
    """
    stepver = '0.1' # pipe step version

    def parse_config(self, path_to_config):
        """
        Parses given database config file for the fits_data table dict within it
        storing a field for every sql field of the table and one designating the primary key.
        Mainly just a convenience wrapper on configobj.ConfigObj to check for 
        a malformed config file. 
        
        Note that fields are from the config file, not the database itself, 
        so if it has changed and the database has not been updated there will be an inconsistency.

        Parameters:
        path_to_config: ini config file for the database. Should contain a [tables] section
        and within that a [[fits_data]] subsection holding a 'primary_key' variable
        and other variables with the name of the desired SQL field mapping to their types.
        Note that this is the config for the database table, not for any pipestep
        
        Returns:
        Returns a dict with a field for every parsed SQL field of the fits_data table mapping
        to their types and another field 'primary_key' mapping to the name of the primary_key
        Raises an error under these circumstances:
        -config file doesn't exist
        -config lacks 'tables' section
        -tables section lacks 'fits_data' subsection
        -no primary key specified in the fits_data table section
        -there aren't at least 2 lines in the fits_data table (must at least specify
        primary key's name and map it to its type)
        """
        config = configobj.ConfigObj(path_to_config, list_values=False, file_error=True)
        self.log.debug(f'Successfully read in database config at {path_to_config}')        
        if 'tables' not in config:
            err_msg = 'Database config lacks tables section!'
            self.log.error(err_msg)
            raise RuntimeError(err_msg)
        elif 'fits_data' not in config['tables']:
            err_msg = 'Database config lacks fits_data table required for stepaddtodatabase!'
            self.log.error(err_msg)
            raise RuntimeError(err_msg)

        fits_data_table = config['tables']['fits_data']
        pk_key = 'primary_key'
        if pk_key not in fits_data_table:
            err_msg = f'Config for fits_data lacks required key {pk_key}!'
            self.log.error(err_msg)
            raise RuntimeError(err_msg)
        elif len(fits_data_table) < 2:
            err_msg = f'Config for fits_data has {len(fits_data_table)} entries; at least 2 required.'
            self.log.error(err_msg)
            raise RuntimeError(err_msg)

        return fits_data_table

    
    def sql_field_to_hdu_field(self, sql_field):
        """
        Given an sql_field that corresponds to an hdu field and follows
        naming convention, will convert it to the corresponding hdu_field.
        
        sql field naming convention mentioned above: take the name of the corresponding HDU field,
        make it lowercase, replace hyphens with underscores, and optionally append a trailing
        underscore (which is required if the application of the other rules turns the 
        HDU field into an an SQL keyword, like with "DEC"). 

        Parameters:
        sql_field: the string name of an sql_field that corresponds to a FITS HDU field
        The field name must follow naming convention which is: take the name of the HDU field,
        make it lowercase, replace hyphens with underscores, and

        Returns:
        Takes an sql field under the name convention described above and returns its HDU field
        counterpart.  
        """
        hdu_field = sql_field.upper().replace('_', '-')
        if hdu_field[-1] == '-':
            return hdu_field[:-1]
        else:
            return hdu_field
    
    def setup(self):
        """ ### Names and Prameters need to be Set Here ###
            Sets the internal names for the function and for saved files.
            Defines the input parameters for the current pipe step.
            Setup() is called at the end of __init__
            The parameters are stored in a list containing the following
            information:
            - name: The name for the parameter. This name is used when
                    calling the pipe step from command line or python shell.
                    It is also used to identify the parameter in the pipeline
                    configuration file.
            - default: A default value for the parameter. If nothing, set
                       '' for strings, 0 for integers and 0.0 for floats
            - help: A short description of the parameter.
        """
        ### Set Names
        # Name of the pipeline reduction step
        self.name='AddToDatabase'
        # Shortcut for pipeline reduction step and identifier for
        # saved file names.
        self.procname = 'unk'
        # Set Logger for this pipe step
        self.log = logging.getLogger('hawc.pipe.step.%s' % self.name)
        ### Set Parameter list
        # Clear Parameter list
        self.paramlist = []
        # Append parameters
        self.paramlist.append(['sql_username', 'default_user',
            'Username for the SQL user to access the database; only add priveleges needed'])
        self.paramlist.append(['sql_password', '',
            ('Password for the SQL user to access the database. Can optionally hold '
            'the path to an existing file which stores only the password')])
        self.paramlist.append(['database_config_path', './pipeconf_dbasereg.txt',
            'Path to database configuration file'])
        self.paramlist.append(['overwrite', False,
            ('If True, when StepAddToDatabase is run on a file that is already in '
            'the database, then it will be overwritten. Requires an SQL user with ' 
            'delete permissions. If overwrite is False and a duplicate file exists, '
            'an error will be thrown.')])

    def run(self):
        """ 
        Connects to the SEO database and adds self.datain to the database's fits_data table.
        Only adds fields described in the database config file, which's path is in the step
        config file. 

        Assumptions:
        -SEO database has been created
        -The file being added is not already in the database or overwrite is True
        If these are violated an error is thrown
        -all database fields in the config file aside from the optional 'file_path' map to 
        FITS HDU fields by the sql_field_to_hdu_field function below (will be true if they 
        follow the convention in the config)
        """
        # Copy datain to dataout (the data doesn't actually have to change)
        self.dataout = self.datain
        # The user should be a mySQL user granted ONLY add permissions
        SQL_user = self.getarg('sql_username')
        SQL_pass = self.getarg('sql_password')
        if path.exists(SQL_pass):
            with open(SQL_pass, 'r') as pass_file:
                # Get rid of accidental new lines
                SQL_pass = pass_file.readline().replace('\n', '')
        database_config_path = self.getarg('database_config_path')
        overwrite = self.getarg('overwrite')
        
        try:
            db = mysql.connect(
                host="localhost",
                user=SQL_user,
                passwd=SQL_pass,
                auth_plugin='mysql_native_password'
            )
        except mysql.errors.ProgrammingError as err:
            err_msg = (f'Encountered error connecting to DB as "{SQL_user}". '
                        'User or pass may be wrong')
            self.log.error(err_msg)
            raise RuntimeError(err_msg) from err
        self.log.info(f'Successfully connected to SQL server as "{SQL_user}"')        
        cursor = db.cursor()

        try:
            cursor.execute('USE seo;')
        except mysql.errors.ProgrammingError as err:
            err_msg = ('Encountered error running SQL command "USE seo". Could mean' 
                      'seo database does not exist for some reason. Perhaps '
                      'create_database.py needs to be run')
            self.log.error(err_msg)    
            cursor.close()
            db.close()
            raise RuntimeError(err_msg) from err

        fits_data_table = self.parse_config(database_config_path)
        pk_key = 'primary_key'
        sql_fields = [sql_field for sql_field in fits_data_table if sql_field != pk_key]
        
        fields_str = ', '.join(sql_fields)
        # Get format specifier for each sql_field; truncate tailing space and comma
        format_specifiers = ('%s, ' * len(sql_fields))[:-2]
        insert_query = f'INSERT INTO fits_data ({fields_str}) VALUES ({format_specifiers});'

        datain_field_vals = []
        if not path.exists(self.datain.filename):
            self.log.warning(
                (f'Starting to add record for {self.datain.filename} to database'
                ' even though os.path.exists for it is False; it has not yet been saved')
            )

        for sql_field in sql_fields:
            if sql_field != 'file_path':
                hdu_field = self.sql_field_to_hdu_field(sql_field)
                # Need val in string form for the below.
                val = self.datain.header[hdu_field] 
                if isinstance(val, bool):
                    datain_field_vals.append(int(val))
                else:
                    datain_field_vals.append(val)
            else:
                datain_field_vals.append(self.datain.filename)

        self.log.debug(
            ('About to attempt to execute the following SQL: '
            f'"{insert_query}" with values "{datain_field_vals}"')
        )

        if overwrite:
            self.log.debug('Duplicate encountered; about to attempt to delete it')
            
            delete_cmd = f'DELETE FROM fits_data WHERE file_path = "{self.datain.filename}";'
            try: 
                cursor.execute(delete_cmd)
            except mysql.errors.ProgrammingError as err:
                err_msg = 'Error trying to overwrite duplicate file; perhaps insufficient privileges'
                self.log.error(err_msg)
                cursor.close()
                db.close()
                raise RuntimeError(err_msg) from err
            self.log.info('Successfully deleted duplicate file from database')
   
        try:
            cursor.execute(insert_query, tuple(datain_field_vals))
            db.commit()
        except mysql.errors.ProgrammingError as err:
            err_msg = 'The error could mean the config file is not up to date with db'
            self.log.error(err_msg)
            cursor.close()
            db.close()
            raise RuntimeError(err_msg) from err
        except mysql.errors.IntegrityError as err:
            err_msg = ('The error likely means the file you are adding to the db '
             'is already there and overwrite was not set.')
            self.log.error(err_msg)
            cursor.close()
            db.close()
            raise RuntimeError(err_msg) from err
        
        self.log.info(f'Successfully added file {self.datain.filename} to the database')
        cursor.close()
        db.close()


    def test(self):
        """ Test Pipe Step Parent Object:
            Runs a adds to the database, checking for errors.
            Should not be run on the actual database as it will add bogus records
        """
        # log message
        self.log.info('Testing pipe step %s' %self.name)
        # log message
        self.log.info('Testing pipe step %s - Done' %self.name)
    
if __name__ == '__main__':
    """ Main function to run the pipe step from command line on a file.
        Command:
          python stepparent.py input.fits -arg1 -arg2 . . .
        Standard arguments:
          --config=ConfigFilePathName.txt : name of the configuration file
          -t, --test : runs the functionality test i.e. pipestep.test()
          --loglevel=LEVEL : configures the logging output for a particular level
          -h, --help : Returns a list of 
    """
    StepAddToDatabase().execute()


""" === History ===
August 3, 2020-First working version created. Assumes file_path is primary key and only non-HDU field.
"""
