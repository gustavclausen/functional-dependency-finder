import sys
import argparse, getpass
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm

# Establish connection to MySQL-database
def establish_db_connection(host, database, user, password):
    try:
        connection = mysql.connector.connect(
            host = host,
            database = database,
            user = user,
            password = password,
            auth_plugin = 'mysql_native_password')
        if connection.is_connected():
            # Successfully connected to database. Return connection
            return connection

    except Error as err:
        # Couldn't connect to database. Print error message with more details
        sys.exit(f'Failed to connect to database:\n{err}')


def get_name_of_tables(db_connection):
    cursor = db_connection.cursor()
    cursor.execute('SHOW TABLES')

    for row in cursor:
        yield row[0] # Return field name


def get_description_of_table(db_connection, table_name):
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(f'DESCRIBE {table_name}')

    fields = []
    primary_keys = []

    for row in cursor:
        field = row['Field']
        fields.append(field)
        
        if (row['Key'] == 'PRI'): # Check if field is primary key in table
            primary_keys.append(field)
    
    return {'fields': fields, 'primary_keys': primary_keys}


def find_func_depend_in_table(db_connection, table_name):
    table_description = get_description_of_table(db_connection, table_name)
    fields = table_description['fields']
    cursor = db_connection.cursor()
    
    func_depends = []
    for i in tqdm(range(0, len(fields)), desc=f'Current table ({table_name})'):
        for j in tqdm(range(i + 1, len(fields)), desc=f'Current field'):
            field_1 = fields[i]
            field_2 = fields[j]
            
            cursor.execute(f'SELECT COUNT(*) FROM {table_name} t1, {table_name} t2 WHERE t1.{field_1} = t2.{field_1} AND t1.{field_2} <> t2.{field_2}')
            count_of_results = cursor.fetchone()[0]
            
            # Functional dependency found: it's not the case that there's more than one value (field_2)
            # associated with field_1
            if (count_of_results == 0):
                func_depends.append(f'{field_1} -> {field_2}')
    
    # Print results
    tqdm.write(f'\n### Results for \'{table_name}\' ###')
    tqdm.write('Primary key(s) in table: ' + ', '.join(map(str, table_description['primary_keys'])))
    tqdm.write('Following functional dependencies found:')
    for fd in func_depends:
        tqdm.write(fd)


class Password:
    DEFAULT = 'Prompt if not specified.'

    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass('Password to database: ')
        self.value = value

    def __str__(self):
        return self.value


# Main method
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('host', action='store', type=str, help='Host running MySQL-database (e.g. localhost)')
    parser.add_argument('database', action='store', type=str, help='Name of database')
    parser.add_argument('-u', '--user', help='Database user', default=getpass.getuser())
    parser.add_argument('-p', '--password', type=Password, help='Password to database', default=Password.DEFAULT)
    args = parser.parse_args()

    db_connection = establish_db_connection(args.host, args.database, args.user, str(args.password))

    try:
        for table in tqdm(list(get_name_of_tables(db_connection)), desc='Overall progress'):
            tqdm.write(f'Now analyzing table \'{table}\'...')
            find_func_depend_in_table(db_connection, table)

    finally:
        db_connection.close()