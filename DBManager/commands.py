import mysql.connector

# La connexion à une base de données en réseau local requiert que celle-ci soit activée en local (par Wamp)
# Connexion to DB in localhost needs it to be activated (by wamp in my case)


def connect(hostname: str = "localhost", username: str = "root", password: str = ""):
    """
    Connects to MySQL
    :param hostname: Name of host
    :param username: Name of user
    :param password: pass
    :return: connection object
    """
    connection = mysql.connector.connect(host=hostname, user=username, password=password)
    return connection


def connect_db(hostname: str = "localhost", username: str = "root", password: str = "", dbname: str = "database"):
    """
    Connects to an existing database
    :param hostname: Name of host
    :param username: Name of user
    :param password: pass
    :param dbname: dbname
    :return: connected db object to be modified
    """
    connection = mysql.connector.connect(host=hostname, user=username, password=password, database=dbname)
    return connection

# The next functions enable us to create queries that are to be executed by a cursor object


def create_db(db_name: str):
    """
    Returns a SQL Command to create a database
    :param db_name: Name of the database to be created
    :return: SQL command as a String
    """
    return "CREATE DATABASE %s" % db_name


def create_table(table_name: str):
    """
    Returns a SQL Command to create a table
    :param table_name: Name of the table
    :return: SQL command as a String
    """
    return "CREATE TABLE %s (id INT AUTO_INCREMENT PRIMARY KEY)" % table_name


def new_column(table_name: str, column_name: str, datatype: str):
    """
    Returns a SQL Command to add a column in a table
    :param table_name:Name of the table
    :param column_name: Name of the column
    :param datatype: Type of data: [varchar(size), bit, tinyint, int, decimal(p,s), float(n), datetime...]
    :return: SQL command as a String
    """
    return "ALTER TABLE %s ADD %s %s" % (table_name, column_name, datatype)


def drop_column(table_name: str, column_name: str):
    """
    Returns a SQL Command to drop a column in a table
    :param table_name: Name of the table
    :param column_name: Name of the column
    :return:
    """
    return "ALTER TABLE %s DROP COLUMN %s" % (table_name, column_name)


def insert_line(table_name: str, **columns: str):
    """
    Returns a SQL Command to insert a line in a table
    :param table_name: Name of the table
    :param columns: column="value" for each column in the table
    :return:SQL command as a String
    """
    column_string = value_string = ""
    for column, value in columns.items():
        if column_string == value_string == "":
            column_string += column
            value_string += value
        else:
            column_string += ", %s" % column
            value_string += ", %s" % value
    return "INSERT INTO %s (%s) VALUES (%s)" % (table_name, column_string, value_string)


def insert_lines(table_name: str, columns: tuple, values: list):
    """
    Returns a SQL Command  and a table to insert many lines in a table
    :param table_name: Name of the table
    :param columns: Tuple of column names
    :param values: Array containing values to insert in Table
    :return: SQL command as a String and an  array of tuples containing data to insert in DB table
    """
    if len(columns) == len(values[0]):
        column_string = value_string = ""
        for column in columns:
            if column_string == "":
                column_string += column
                value_string += "%s"
            else:
                column_string += ", %s" % column
                value_string += ", %s"
        val = []
        for value in values:
            val.append(tuple(value))
        return "INSERT INTO %s (%s) VALUES (%s)" % (table_name, column_string, value_string), val


def select_table(table_name: str):
    return "SELECT * FROM %s" % table_name


a = [["a", "b"], ["c", "d"]]

print(insert_lines("a", ("name", "surname"), a))

# print(a)
# print(tuple(a))
