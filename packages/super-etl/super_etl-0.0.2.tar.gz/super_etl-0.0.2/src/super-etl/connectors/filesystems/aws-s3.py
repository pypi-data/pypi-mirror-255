# -*- coding: UTF-8 -*-
#######################################
# Amazon AWS S3 Filesystem
#######################################
#
# Principle: https://aws.amazon.com/s3/
# Library: boto3 (https://boto3.amazonaws.com/v1/documentation/api/latest/)
# Author: Rik Heijmann
#

from logger import log
import boto3 


####################
# General
####################
def create_connection(accessKeyId, secretAccessKey, region, arn, rolesession):
    # Example Region: eu-west-1
    client = boto3.client('sts', region,aws_access_key_id=accessKeyId,aws_secret_access_key=secretAccessKey)

    # Example ARN: arn:aws:iam::373434216115:role/external-developer-role-eu-west-1"
    # Example Rolesession: AssumeRoleSession1
    assumed_role_object=client.assume_role(
        RoleArn=arn,
        RoleSessionName=rolesession
    )

    credentials=assumed_role_object['Credentials']

    connection=boto3.resource(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )

    return connection

# TODO: Add function to display all the available buckets.


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