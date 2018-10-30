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
    result = cursor.fetchall()

    if not result:
        raise Error(f'Table {table_name} couldn\'t be found.')

    fields = []
    primary_keys = []

    for row in result:
        field = row['Field']
        fields.append(field)
        
        if row['Key'] == 'PRI': # Check if field is primary key in table
            primary_keys.append(field)
    
    return {'fields': fields, 'primary_keys': primary_keys}


def find_func_depend_in_table(db_connection, table_name):
    table_description = get_description_of_table(db_connection, table_name)
    fields = table_description['fields']
    cursor = db_connection.cursor(buffered=True)

    tqdm.write(f'\nNow analyzing table \'{table_name}\'...')

    func_depends = []
    for i in tqdm(range(0, len(fields)), desc=f'Current table ({table_name})'):
        for j in tqdm(range(0, len(fields)), desc=f'Current field'):
            if (i == j):
                continue

            field_1 = fields[i]
            field_2 = fields[j]
            
            cursor.execute(f'SELECT {field_1}, COUNT(DISTINCT {field_2}) c FROM {table_name} GROUP BY {field_1} HAVING c > 1')

            # Functional dependency found: it's not the case that there's more than one value (field_2)
            # associated with field_1
            if (cursor.rowcount == 0):
                func_depends.append(f'{field_1} -> {field_2}')
    
    # Print results
    tqdm.write(f'\n### Results for \'{table_name}\' ###')
    tqdm.write('Primary key(s) in table: ' + ', '.join(map(str, table_description['primary_keys'])))
    if func_depends:
        tqdm.write('Following functional dependencies found:')
        for fd in func_depends:
            tqdm.write(fd)
    else:
        tqdm.write('No functional dependencies found.')


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
    parser.add_argument('-t','--tables', nargs='+', help='Pick which tables to examine', default='all')
    args = parser.parse_args()

    db_connection = establish_db_connection(args.host, args.database, args.user, str(args.password))

    try:
        tables_to_examine = list(get_name_of_tables(db_connection)) if args.tables == 'all' else args.tables

        for table in tqdm(tables_to_examine, desc='Overall progress'):
            find_func_depend_in_table(db_connection, table)
    
    except Error as err:
        sys.exit(f'An error occurred:\n{err}\nExiting...')

    finally:
        db_connection.close()