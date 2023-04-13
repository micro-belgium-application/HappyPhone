from .connection.api_fetch import Connection
from .cleaning.cleaning_data import Clean
from .database.export_to_sql import SQL
from  .logger.logger import Logger
from .logger.log_contacts import LogContacts
import time
import os
import yaml

module_path = os.path.dirname(os.path.dirname(__file__))

rel_path_config = '/config.yml'
abs_path_config = module_path + rel_path_config

with open(abs_path_config, 'r') as file:
    config = yaml.safe_load(file)
time_between_fetches = config['parameters']['time_between_fetches']
writeLogs = config['parameters']['writeUnnamedContactsIntoLogs']


def run():
    """
    Executed when app is run in shell
    """ 
    print("------- Google Contacts Sync --------- ")
    
    connection = Connection()


    while True :
        
        total_seconds = time_between_fetches

        Logger(5)
        routine(connection)

        for i in range(total_seconds):
            time.sleep(1)
            print(f"Wait for {total_seconds-(i+1)} seconds ")



def routine(connection):
    """
    Routine :
    - fetch contacts from google api
    - clean contacts 
    - log unnamed contacts
    - export to SQL
    """
    
    contacts, groups, email, other_contacts = connection.fetch_all()
    
    # cleaned_contacts and other_contacts_clean are Tuples of type (cleaned : List, unnamed : List)
    cleaned_contacts, cleaned_groups, other_contacts_cleaned = Clean(contacts, groups, email, other_contacts).get_clean_data()
    
    # Logs contacts
    if writeLogs == True:
        LogContacts(cleaned_contacts,other_contacts_cleaned)

    # Export to sql
    SQL(cleaned_contacts, cleaned_groups,other_contacts_cleaned)
    
