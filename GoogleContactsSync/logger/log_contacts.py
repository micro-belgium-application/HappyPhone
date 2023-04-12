import datetime
from logging import Logger
from os.path import dirname as dir
import os
import pyodbc
import yaml

logs_path = (dir(dir(dir(__file__))) + '/logs/').replace('\\', '/')

module_path = os.path.dirname(os.path.dirname(__file__))
rel_path_config = '/config.yml'
abs_path_config = os.path.dirname(module_path) + rel_path_config

class LogContacts:
    def __init__(self, contacts: list, other_contacts: list, groups = []):
        """
        Args : contacts, groups, other contacts (type -> list)
        Return : None
        Logs unnamed contacts
        """
        self.unnamed_contacts = []
        try:
            if contacts is not None:  
                self.unnamed_contacts += contacts[1]
            if other_contacts is not None:
                self.unnamed_contacts += other_contacts[1]
        except Exception as e:
            print(f"There was an error while logging contacts: \n{e}")

        if len(self.unnamed_contacts) >0 :
            Logger(7,len(self.unnamed_contacts))
            self.write_unnamed_contacts_to_file()



    def write_unnamed_contacts_to_file(self):
        """
        Args: unnamed_contacts (type -> list)
        Return : None
        Creates a log with all contacts without any name
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        contacts_string = str(self.unnamed_contacts)

        try:
            with open(logs_path + str(today) + '__unnamed_contacts.txt', 'w') as file:
                file.write(contacts_string)
            print(f"Added unnamed contacts to logs : {len(self.unnamed_contacts)}")
        except Exception as e:
            print(f"Error while write logs :{e}")
