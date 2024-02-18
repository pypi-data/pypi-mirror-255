# -*- coding: UTF-8 -*-
#######################################
# FTP Filesystem
#######################################
#
# Principle: https://en.wikipedia.org/wiki/File_Transfer_Protocol
# Library: ftplib (https://docs.python.org/3/library/ftplib.html)
# Author: Rik Heijmann
#

from logger import log
import ftplib


####################
# Extract
####################

# TODO: Add connection.cwd to change directory. Or allow users to use a full URL. 
# TODO: Add exceptions.


def get_file(host, port, user, password, url, filename):
    connection = ftplib.FTP(host, user, password)
    connection.port(port)
    connection.encoding = "utf-8"

    with open("./downloads/" + filename, 'wb') as file:
        connection.retrbinary(filename, file.write)

    connection.quit()
