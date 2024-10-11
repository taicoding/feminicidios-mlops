import os
from dagster import OpExecutionContext
from dagster_shell import execute_shell_command

def index_exists(collection, index_name):
    indexes = collection.list_indexes()
    for index in indexes:
        if index['name'] == index_name:
            return True
    return False