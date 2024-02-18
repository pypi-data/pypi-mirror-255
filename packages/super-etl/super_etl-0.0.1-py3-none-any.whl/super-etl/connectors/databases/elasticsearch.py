# -*- coding: UTF-8 -*-
#######################################
# ElasticSearch connector
#######################################
#
# Principle: https://www.elastic.co/elasticsearch/
# Library: elasticsearch (https://github.com/elastic/elasticsearch-py)
# Author: Rik Heijmann
#

from logger import log
import elasticsearch
from ssl import create_default_context
import modin.pandas as pandas


##########################
# Script:
##########################
# Creates a SSL context. Which allows us to temporary disable SSL certificate verification.
def create_connection(host, port, user, password, ssl, verifyssl):
    connection = None
    if ssl == True:
        scheme = "https"
    else:
        scheme = "http"

    try:
        ssl_context = create_default_context()
        if verifyssl == False:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        # Connect to ElasticSearch and create a cursor.
        connection=elasticsearch.Elasticsearch(host = host, port = port, http_auth=(user, password), scheme=scheme, ssl_context=ssl_context, http_compress=True, timeout=30, max_retries=10, retry_on_timeout=True)

    except elasticsearch.ElasticsearchException as error:
        log(f"Error while connecting to ElasticSearch: {error}", "error")
    else:
        # Test if the cursor works.
        if connection.ping():
            return connection

def check_table(connection, table):
    try:
        answer = connection.indices.exists(index=table)
    except elasticsearch.ElasticsearchException as error:
        log(f"ElasticSearch: Failed to check if index [{table}] existst: {error}", "error")
    else:
        return answer

####################
# Extract
####################
def get_data(connection, query):
# A Function to export data out of ElasticSearch. Currently limited at 1000 records.
    doc_count = 0
    data_dict = []

    # Declare a filter query that searches for the documents that should be exported. Match_all is required to select all documents within a index. The size-paramters is required, its maximum is predefined. In the default situation this has been set to 10.000 hits.
    filter = {
            "size": batch_size,
            "query": {
                "match_all": {}  
            }
    }
    
    # Make a search() request to get all docs in the index, while opening a scroll session. This session allows us to receive the next in-line hits 
    resp = source_elasticsearch_cursor.search(
            index = source_elasticsearch_index,
            body = filter,
            scroll = '10m' # Length of time to keep search context.
    )

    # Keep track of past scroll-id
    old_scroll_id = resp['_scroll_id']

    # Use a 'while' iterator to loop over the amount of document 'hits'.
    while len(resp['hits']['hits']):
        batches -= 1

        # Make a request using the Scroll API while reusing the original Scroll-API-ID
        resp = source_elasticsearch_cursor.scroll(
            scroll_id = old_scroll_id,
            scroll = '2s' # Length of time to keep search context. Please extend this if the cluster takes to long to respond. As it might end the original session. 
        )

        # Check if there's a new Scroll-API-ID.
        if old_scroll_id != resp['_scroll_id']:
            print ("New scroll ID:", resp['_scroll_id'])

        # Keep track of past Scroll-API-ID.
        old_scroll_id = resp['_scroll_id']


        for doc in resp['hits']['hits']: # Iterate over the document hits for each 'Scroll'-API-session.
            temp_dict = {  # Dictinary that contains instructions for the indexing process. This format is needed to execute "elasticsearch.helpers.bulk". Which takes a list of commands with their parameters.
                "_index": f'{destination_elasticsearch_index}', # The name of the destination index.
                "_type": '_doc',
                "_id": doc['_id'] # The ID of the original document. Can be preserved. Should be in some cases.
            }
            for key in doc['_source']: # Migrate all of the original data into the temporary dictionary.
                temp_dict[key] = doc['_source'][key] # It has to be done by looping through the dictionary, while inserting each value into a new key of the temporary dictionary.
            
            temp_dict = transformDocument(temp_dict)

            data_dict.append(temp_dict) # Add the temporary dictionary to the data_dict. Which is actually a list with each document.

            doc_count += 1
            # print(f"Currently at {doc_count}, doc-id: {doc['_id']}.")
        
        print(f"Currently at {doc_count}, doc-id: {doc['_id']}.")
        time.sleep(waittime_per_export_iteration)

        if batches == 0 and limit_batches == True:
            break
    return(data_dict)
