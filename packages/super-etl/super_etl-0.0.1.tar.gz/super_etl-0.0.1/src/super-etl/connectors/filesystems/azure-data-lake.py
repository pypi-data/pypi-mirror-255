# -*- coding: UTF-8 -*-
#######################################
# Microsoft Azure Data Lake filesystem
#######################################
#
# Principle: https://en.wikipedia.org/wiki/File_Transfer_Protocol
# Library: boto3 (https://boto3.amazonaws.com/v1/documentation/api/latest/)
# Author: Rik Heijmann
#

from logger import log
import os, uuid, sys
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings


####################
# General
####################
def create_connection(storageAccountName, storageAccountKey, https):
    if https:
        protocol = "https"
    else:
        protocol = "http"

    try:
        client = DataLakeServiceClient(account_url=f"{protocol}://{storageAccountName}.dfs.core.windows.net".format, credential=storageAccountKey)
    
    except Exception as error:
        print(e)

    else:
        return client


# TODO: Add function to display all the available files.


####################
# Extract
####################
def get_file(connection, bucket, filename):
    path = "./downloads/" + filename
    connection.meta.client.download_file(bucket, filename, path)

def get_all_files(connection):
    path = []
    for obj in connection.Bucket('bucket').objects.all():
        filename = obj.key.replace("\\", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(":", "-")
        path = "./downloads/" + filename
        paths = paths.append(path)
        connection.meta.client.download_file(obj.bucket_name, obj.key, path)