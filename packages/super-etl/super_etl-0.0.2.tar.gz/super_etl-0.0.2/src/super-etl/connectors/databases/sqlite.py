# -*- coding: UTF-8 -*-
#######################################
# SQLite connector
#######################################
#
# Principle: https://sqlite.org/index.html
# Library: sqlite3 (https://github.com/coleifer/pysqlite3)
# Author: Rik Heijmann
#

from logger import log
from os.path import exists
import sqlite3
import datetime
import time
import modin.pandas as pandas

sql_create_table_metadata = """
        CREATE TABLE metadata (
                metadata_id INTEGER PRIMARY KEY,
                timestamp TEXT,
                timezone REAL,
                version REAL,
                action TEXT,
        )
        """


#####################
# General
#####################
def create_connection(file):
    connection = None
    try:
        connection = sqlite3.connect(file)
    except sqlite3.Error as error:
        log(f"SQLite: Failed to create a database: {error}", "error")
    return connection

def check_table(connection,schema,table):
    try:
        cursor = connection.cursor()
        sql = f"""
            SELECT tableName FROM sqlite_master
            WHERE type='table' AND tableName  = '{table}'
            """
        cursor.execute(sql)
        results = cursor.fetchall()[0]
        if len(results) > 0:
            answer = True
        else:
            answer = False
        cursor.close()

    except sqlite3.Error as error:
        log(f"SQLite: Failed to check if table [{table}] exists: {error}", "error")
    finally:
        return answer
    

####################
# Extract
####################
def get_data(connection, query):
    return pandas.read_sql_query(query, connection)


####################
# Load
####################
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_create_table_metadata)
        connection.commit()
        timestamp = datetime.datetime.now()
        timestamp_unix = time.mktime(timestamp.timetuple())
        ts = time.time()
        timezone = datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)
        timezone_seconds = timezone.total_seconds()
        info = (timestamp_unix, timezone_seconds, "The cachedatabase has been created.")
        sql = f''' INSERT INTO metadata(timestamp,timezone,operation) VALUES(?,?,?);'''
        cursor.execute(sql,info)
    except sqlite3.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"SQLite: Failed to create a database: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"SQLite: Failed to create a table: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def delete_table(connection, table):
    try:
        sql = f"DROP TABLE {table};"
        cursor = connection.cursor()
        cursor.execute(sql)
    except sqlite3.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"SQLite: Failed to delete table [{table}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def empty_table(connection, table):
    try:
        sql = f"DELETE FROM {table}", f"DELETE FROM sqlite_sequence WHERE name='{table};'"
        cursor = connection.cursor()
        cursor.execute(sql)
    except sqlite3.Error as error:
        cursor.rollback()
        cursor.close()
        log(f"SQLite: Failed to empty table [{table}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()


####################
# Metadata
####################
def insert_metadata(connection, data):
    try:
        table = "metadata"
        sql = f''' INSERT INTO {table}(timestamp,timezone,action) VALUES(?,?,?);'''
        cursor = connection.cursor()
        cursor.execute(sql, data)
    except sqlite3.Error as error:
        cursor.rollback()
        cursor.close()
        log("SQLite: Failed to write metadata: {error}", "error")
    else:
        cursor.commit()
        cursor.close()