# -*- coding: UTF-8 -*-
#######################################
# MySQL connector
#######################################
#
# Principle: https://www.mysql.com/
# Library: mysql.connector (https://github.com/mysql/mysql-connector-python)
# Author: Rik Heijmann
#

from logger import log
import mysql.connector
import modin.pandas as pandas


#####################
# General
#####################
def create_connection(host, port, user, password):
    connection = None
    try:
        connection = mysql.connector.connect(host=host,
                                            port=port,
                                            user=user,
                                            password=password)        
    except mysql.connector.Error as error:
        print(f"Error while connecting to MySQL: {error}")
    else:
        if connection.is_connected():
            return connection

def check_table(connection,database,table):
    try:
        cursor = connection.cursor()
        sql = f"""
            SELECT COUNT(*) FROM information_schema.tables WHERE table_name  = '{table}';
            """
        cursor.execute(sql)
        result = cursor.fetchall()[0]
        if result > 0:
            answer = True
        else:
            answer = False
        cursor.close()
    except mysql.connector.Error as error:
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
    except mysql.connector.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MySQL: Failed to create database [{database}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()      

def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except mysql.connector.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MySQL: Failed to create a table: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def empty_table(connection, table):
    try:
        cursor = connection.cursor()
        sql = f"TRUNCATE TABLE {table};"
        cursor.execute(sql)
        cursor.close()
    except mysql.connector.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"MySQL: Failed to empty table [{table}]: {error}", "error")
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
              VALUES(%s, %s, %s) '''
        cursor = connection.cursor()
        cursor.execute(sql, data)
    except mysql.connector.Error as error:
        cursor.rollback()
        cursor.close()
        log("MySQL: Failed to write metadata: {error}", "error")
    else:
        cursor.commit()
        cursor.close()