# -*- coding: UTF-8 -*-
#######################################
# MartiaDB connector
#######################################
#
# Principle: https://mariadb.org/
# Library: mariadb (https://github.com/mariadb-corporation/mariadb-connector-python)
# Author: Rik Heijmann
#

from logger import log
import mariadb
import modin.pandas as pandas


#####################
# General
#####################
def create_connection(host, port, user, password):
    connection = None
    try:
        connection = mariadb.connect(host=host,
                                            port=port,
                                            user=user,
                                            password=password)
    except mariadb.Error as error:
        print(f"Error while connecting to MariaDB: {error}")
    else:
        if connection.is_connected():
            return connection

def check_table(connection,database,table):
    try:
        cursor = connection.cursor()
        sql = f"""
            SELECT EXISTS (
                SELECT TABLE_NAME
            FROM
                information_schema.TABLES
            WHERE
                TABLE_SCHEMA = {table}
            );
            """
        cursor.execute(sql)
        answer = cursor.fetchall()[0]
        cursor.close()
    except mariadb.Error as error:
        log(f"MariaDB: Failed to check if table [{database}.{table}] existst: {error}", "error")
    else:
        return answer


####################
# Extract
####################
def get_data(connection, query):
    return pandas.read_sql(query, connection)

####################
# Load
####################
def create_database(connection, database):
    try:
        cursor = connection.cursor()
        sql = f"CREATE DATABASE {database};"
        cursor.execute(sql)
    except mariadb.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MariaDB: Failed to create database [{database}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except mariadb.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MariaDB: Failed to create a table: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def empty_table(connection, table):
    try:
        cursor = connection.cursor()
        sql = f"TRUNCATE TABLE {table};"
        cursor.execute(sql)
        cursor.close()
    except mariadb.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MariaDB: Failed to empty table [{table}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()


####################
# Metadata
####################
def insert_metadata(connection, data):
    try:
        table = "metadata"
        sql = f''' INSERT INTO {table}(timestamp,timezone,action)
              VALUES(?, ?, ?) '''
        cursor = connection.cursor()
        cursor.execute(sql, data)
    except mariadb.Error as error:
        cursor.rollback()
        cursor.close()
        log("MariaDB: Failed to write metadata: {error}", "error")
    else:
        cursor.commit()
        cursor.close()
