import pyodbc
#from .database_settings import DATABASE_CONNECTION, DATABASE
import yaml
import os 
from .sql_commands import *
from ..logger.logger import Logger
import time

module_path = os.path.dirname(os.path.dirname(__file__))

rel_path_config = '/config.yml'
abs_path_config = os.path.dirname(module_path) + rel_path_config

class SQL:

    def __init__(self, contacts, groups, other_contacts):
        """
        Args : contacts, groups, other contacts (type -> list)
        Return : None
        Class constructor that creates a connection to the db, and then calls functions to push every type of data to it
        """
        if contacts == [] and groups == [] and not other_contacts:
            return
        elif contacts is None and groups is None and other_contacts is None:
            return
        else:
            try :
                with open(abs_path_config, 'r') as file:
                    config = yaml.safe_load(file)

                connection_params = config["database_settings"]["database_connection"].strip()
                self.connection = pyodbc.connect(connection_params)

                print("Succesfully connected")
                
                # Wait 0.5 sec to temporize
                time.sleep(0.5)

                # Create a cursor object to execute SQL statements
                self.cursor = self.connection.cursor()

                if contacts is not None:
                    self.contacts = contacts[0]
                if groups is not None:
                    self.groups = groups
                if other_contacts is not None:
                    self.other_contacts = other_contacts[0]

                # Execute commands
                self.push_groups_to_sql()
                self.push_contacts_to_sql()
                self.push_other_contacts_to_sql()

                print("Sucessfully pushed changes to DB")

                # Close the cursor and connection objects
                self.cursor.close()
                self.connection.close()
                Logger(4, config["database_settings"]['database'])
            except Exception as err :
                Logger(-1, err)
                print(f"There was error while connecting : \n {err}")
    def push_groups_to_sql(self):
        """
        Args : None
        Returns : None
        Pushes groups to SQL db
        """
        if not self.groups :
            return
        else :
            try :
                print(f"Number of groups modified: {len(self.groups)}")
                self.push_to_GGroup(self.groups)
            except pyodbc.DatabaseError as err:
                self.connection.rollback()
                self.connection.close()
                Logger(-1, err)
                print(f"There was an error while committing changes: Rolling back \n {err}")
            finally:
                self.connection.commit()
                print("Changes committed successfully for groups")
    def push_other_contacts_to_sql(self):
        """
        Args : None
        Returns : None
        Pushes other_contacts to SQL db
        """
        if not self.other_contacts :
            return 
        else :
            try : 
                print(f"Number of other contacts modified: {len(self.other_contacts)}")
                for other_contact in self.other_contacts :
                    pk = self.push_to_GContactFeed(other_contact)
                    self.push_to_all_tables(pk, other_contact)
            except pyodbc.DatabaseError as err:
                self.connection.rollback()
                self.connection.close()
                Logger(-1, err)
                print(f"There was an error while committing changes: Rolling back \n {err}")
            finally:
                self.connection.commit()
                print("Changes committed successfully for other contacts") 
    def push_contacts_to_sql(self):
        """
        Args : None
        Returns : None
        Pushes contacts to SQL db
        """
        if not self.contacts :
            return 
        else :
            try:
                print(f"Number of contacts modified: {len(self.contacts)}")
                i = 0
                for contact in self.contacts:
                    pk = self.push_to_GContactFeed(contact)
                    self.push_to_all_tables(pk, contact)
                    i+=1
            except pyodbc.DatabaseError as err:
                self.connection.rollback()
                self.connection.close()
                Logger(-1, err)
                print(f"There was an error while committing changes: Rolling back \n {err}")
            finally:
                self.connection.commit()
                print("Changes committed successfully for contacts")
        
    def push_to_all_tables(self,pk, contact):
        """
        Args: idContact (pk), contact (type -> int, dict)
        Return : None
        Pushes contact to all tables
        """
        try :
            self.delete_from_tables(pk)
            self.push_to_GGroupContact(pk, contact)
            self.push_to_GAddress(pk, contact)
            self.push_to_GEmail(pk, contact)
            self.push_to_GNumPhone(pk, contact)
            self.push_to_GUserDefinedField(pk, contact)
            self.push_to_GPhoneNumbers(pk,contact)
        except Exception as e :
            Logger(-1, e)
            print(e)
            raise e 
    def push_to_GContactFeed(self, contact):
        """
        Args: contact (type -> list)
        Return : idContact (pk) (type -> int)
        Pushes contact to GContactFeed and return it's primary key
        """
        try : 
            # @accountSrc=?, @gFeed=?, @lastUpdated=?, @lastSync=?, @fullname=?, @lastname=?, @name=?, @memo=?, @jobTitle=?, @company=?
            useful_params = (contact['accountSrc'], contact['id'], contact['lastModified'], contact['lastSync'], contact['fullname'], contact['lastname'], contact['name'], contact['about'], contact['title'], contact['company'], contact['deleted'], contact['raw_json'], contact['etag'])
            pk = self.cursor.execute(PROCEDURE_GContactFeed, useful_params).fetchval()
            return pk
        except Exception as e:
            Logger(-1, e)
            print(f"Error while pushing GContactFeed : {e}")
            pass
    def push_to_GGroup(self, groups):
        """
        Args: groups (type -> list)
        Return : None
        Pushes groups to GGroup
        """
        try :
            # ['resourceName','accountSrc','name', 'groupType', 'lastUpdated', 'lastSync', 'deleted']
            for group in groups :
                self.cursor.execute(PROCEDURE_GGroup, group)
        except Exception as e:
            Logger(-1, e)
            pass


    def push_to_GGroupContact(self, pk, contact):
        """
        Args: idContact (pk), contact (type -> list)
        Return : None
        Links contact and it's groups by pushing it to GGroupContact table
        """
        if contact['groups']:
            try :
                for group_id in contact['groups']:
                    useful_params = (pk, group_id, contact['accountSrc'])
                    self.cursor.execute(PROCEDURE_GGroupContact, useful_params)
            except Exception as e:
                    Logger(-1, e)
                    pass
        else :
            pass
    def delete_from_tables(self, pk):
        """
        Args : idContact (pk) (type -> int)
        Return: None
        Deletes all previous records in all tables linked to this idContact
        """
        self.cursor.execute(PROCEDURE_delete_from_tables, pk)
    def push_to_GAddress(self, pk, contact):
        """
        Args : idContact (pk), contact (type -> int, list)
        Return : None
        Pushes for this idContact it's addresses to GAddresses table
        """
        if contact['addresses']:
            for address in contact['addresses']:
                try :
                    # ['type', 'street', 'city', 'region' , 'postCode', 'country', 'idContact']
                    useful_params = (address[0], address[1], address[2], address[3], address[4], address[5], pk)
                    self.cursor.execute(PROCEDURE_GAddress, useful_params)
                except Exception as e:
                    Logger(-1, e)
                    pass
        else :
            pass
    def push_to_GEmail(self, pk,  contact):
        """
        Args : idContact (pk), contact (type -> int, list)
        Return : None
        Pushes for this idContact it's emails to GEmails table
        """
        if contact['emails']:
            for email in contact['emails'] :
                try :
                    # ['value', 'type' , idContact]
                    useful_params = (email[0], email[1], pk)
                    self.cursor.execute(PROCEDURE_GEmail, useful_params)
                except Exception as e:
                    Logger(-1, e)
                    pass
        else : 
            pass
    def push_to_GNumPhone(self, pk, contact):
        """
        Args : idContact (pk), contact (type -> int, list)
        Return : None
        Pushes for this idContact it's phone numbers to GNumPhones tables 
        """
        if contact['phoneNumbers']:
            for phone in contact['phoneNumbers']:
                try :
                    # ['value', 'type', idContact]
                    useful_params = (phone[0], phone[1],pk)
                    self.cursor.execute(PROCEDURE_GNumPhone, useful_params)
                except Exception as e:
                    Logger(-1, e)
                    pass
        else :
            pass
    def push_to_GUserDefinedField(self, pk, contact) :
        """
        Args : idContact (pk), contact (type -> int, list)
        Return : None
        Pushes for this idContact it's user defined fields to GUserDefinedField table 
        """
        if contact['userDefined']:
            for field in contact['userDefined']:
                try :
                    #[idContact, 'key','value']
                    useful_params = (pk, field[0], field[1])
                    self.cursor.execute(PROCEDURE_GUserDefinedField, useful_params)
                except Exception as e:
                    Logger(-1, e)
                    pass
        else :
            pass
    
    def push_to_GPhoneNumbers(self, pk, contact):
        """
        Args : idContact (pk), contact (type -> int, list)
        Return : None
        Pushes for this idContact it's phone numbers to GNumPhones tables 
        """
        if contact['phoneNumbersNEW']:
            for phone in contact['phoneNumbersNEW']:
                try :
                    logs = None
                    msg = ""
                    if (len(phone[0]) <=8 or len(phone[0]) >= 20):
                        msg += "WARN:phone encoding;"
                    if (phone[4] is None):
                        msg += "WARN:no type"
                    elif ( len(phone[4]) >= 15):
                        msg += "WARN:type encoding"
                       
                    if len(msg) != 0:
                        logs = msg
                    # ['value','canonicalForm','integerForm','bigIntegerForm', 'type','idGoogle', idContact, logs] corresponding to :  @rawPhone=?,  @canonicalForm=?, @integerForm=?, @type=?, @idGoogle=? @idContact=? @logs
                    useful_params = (phone[0], phone[1], phone[2],phone[3],phone[4],phone[5],pk, logs)

                    self.cursor.execute(PROCEDURE_GPhoneNumbers, useful_params)
                except Exception as e:
                    Logger(-1, e)
                    print(f"Error while pushing GPhoneNumbers : {e}")
                    pass
        else :
            pass

