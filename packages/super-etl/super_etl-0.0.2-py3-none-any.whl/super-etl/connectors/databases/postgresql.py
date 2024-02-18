# -*- coding: UTF-8 -*-
#######################################
# PostgreSQL connector
#######################################
#
# Principle: https://www.postgresql.org/
# Library: psycopg2 (https://www.psycopg.org/)
# Author: Rik Heijmann
#

from logger import log
import psycopg2
import modin.pandas as pandas


#####################
# General
#####################
def create_connection(host, port, user, password):
    connection = None
    try:
        # connect to the PostgreSQL server
        connection = psycopg2.connect(host=host, port=port, user=user, password=password))
    except (Exception, psycopg2.DatabaseError) as error:
        log(f"PostgreSQL: Failed to create the weatherreport table: {error}", "error")
    else:
        if connection is not None:
            return connection


def check_table(connection,database,table):
    try:
        cursor = connection.cursor()
        sql = f"""
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE  schemaname = '{database}'
                AND    tablename  = '{table}'
            );
            """
        cursor.execute(sql)
        answer = cursor.fetchall()[0]
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        log(f"PostgreSQL: Failed to check if table [{database}.{table}] existst: {error}", "error")
    else:
        return answer


####################
# Extract
####################
def get_data(connection, query):
    return pandas.io.sql.read_sql_query(query, connection)


####################
# Load
####################
def create_database(connection, database):
    try:
        cursor = connection.cursor()
        sql = f"CREATE DATABASE {database};"
        cursor.execute(sql)
    except (Exception, psycopg2.DatabaseError) as error:
        cursor.rollback()
        cursor.close()
        log(f"PostgreSQL: Failed to create database [{database}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()      

def create_table(connection, create_table_sql):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except (Exception, psycopg2.DatabaseError) as error:
        cursor.rollback()
        cursor.close()
        log(f"PostgreSQL: Failed to create a table: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def delete_table(connection, table):
    try:
        cursor = connection.cursor()
        sql = f"DROP TABLE {table};"
        cursor.execute(sql)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        cursor.rollback()
        cursor.close()
        log(f"PostgreSQL: Failed to delete table [{table}]: {error}", "error")
    else:
        cursor.commit()
        cursor.close()

def empty_table(connection, table):
    try:
        cursor = connection.cursor()
        sql = f"TRUNCATE TABLE {table};"
        cursor.execute(sql)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        cursor.rollback()
        cursor.close()
        log(f"PostgreSQL: Failed to empty table [{table}]: {error}", "error")
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
              VALUES({data}) '''
        cursor = connection.cursor()
        cursor.execute(sql)
    except (Exception, psycopg2.DatabaseError) as error:
        cursor.rollback()
        cursor.close()
        log("PostgreSQL: Failed to write metadata: {error}", "error")
    else:
        cursor.commit()
        cursor.close()