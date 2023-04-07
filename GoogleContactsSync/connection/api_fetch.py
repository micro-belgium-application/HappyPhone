import os 
import datetime
import itertools
import yaml
from ..logger.logger import Logger

from google.oauth2 import service_account

#from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build 


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.

module_path = os.path.dirname(os.path.dirname(__file__)).replace("\\","/")

rel_path_config = '/config.yml'
abs_path_config = os.path.dirname(module_path) + rel_path_config

with open(abs_path_config, 'r') as file:
    config = yaml.safe_load(file)
account_email = config['account']['email'].strip()
ignoreSyncTokens = config['parameters']['ignoreSyncTokens']
syncOtherContacts = config['parameters']['syncOtherContacts']
maxSyncHours = config['parameters']['maxSyncHours']

rel_path_bot_secrets = '/secrets/client_secret.json'
abs_path_bot_secrets = module_path + rel_path_bot_secrets

rel_path_syncTokenContacts = '/connection/syncTokenContacts.py'
abs_path_syncTokenContacts = module_path + rel_path_syncTokenContacts

rel_path_syncTokenGroups= '/connection/syncTokenGroups.py'
abs_path_syncTokenGroups = module_path + rel_path_syncTokenGroups

rel_path_syncTokenOtherContacts = '/connection/syncTokenOtherContacts.py'
abs_path_syncTokenOtherContacts = module_path + rel_path_syncTokenOtherContacts

# This access scope grants read-only access to the authenticated user's Contacts
# ,'https://www.googleapis.com/auth/contacts.other.readonly'
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly','https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/contacts.other.readonly']

# Which API to fetch
API_SERVICE_NAME = 'people'
API_VERSION = 'v1'

# Which fields to get from People API
PERSON_FIELDS = "names,phoneNumbers,memberships,addresses,organizations,userDefined,emailAddresses,biographies,metadata"
READ_MASK = "names,emailAddresses,phoneNumbers"



class Connection:

    def __init__(self):
        """
        Args : None
        Return : None
        Class constructor, resets class properties and establishes connection 
        """

        Logger(6,account_email)

        self.contacts = []

        self.groups = []

        self.other_contacts = []

        self.syncTokenContacts, self.syncTokenGroups, self.syncTokenOtherContacts = None, None, None

        print("Establishing connection...")

        self.service = self.get_authenticated_service()
        
        print("Connection established !")
        
    def get_authenticated_service(self) :
        """
        Args : None
        Return : Resource object, constructed with the correct version of the api, it's name and credentials object
        Uses the service account created for the project (important to grant the correct scopes in the admin console for the GSuiteDomain, delegating domain-wide authority in the IAM console)
        and it's credentials (to download from https://console.cloud.google.com/apis/credentials) to impersonate the real account and make requests on it's behalf
        (Not practical, so not used anymore : Establishes the connection using OAuth2.0, opens the browser for you, so only needs confirmation from user)
        """
        # flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        # credentials = flow.run_local_server(host='localhost', port=8080, authorization_prompt_message='Please visit this URL: {url}', 
        #    success_message='The auth flow is complete; you may close this window.',
        #    open_browser=True)  
        credentials = service_account.Credentials.from_service_account_file(abs_path_bot_secrets, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(account_email)
        
        return build(API_SERVICE_NAME, API_VERSION, credentials=delegated_credentials)

    def save_syncToken_other_contacts(self, token):
        """
        Args : syncToken for other contacts (type -> str)
        Return : None
        Saves the syncToken for other contacts, and the time it was fetched
        """
        with open(abs_path_syncTokenOtherContacts, "w+") as file :
            file.writelines([token+"\n",str(datetime.datetime.now())])

    def save_syncToken_contacts(self, token):
        """
        Args : syncToken for contacts (type -> str)
        Return : None
        Saves the syncToken for contacts, and the time it was fetched
        """
        with open(abs_path_syncTokenContacts, "w+") as file :
            file.writelines([token+"\n",str(datetime.datetime.now())])

    def save_syncToken_groups(self, token):
        """
        Args : syncToken for groups (type -> str)
        Return : None
        Saves the syncToken for groups, and the time it was fetched
        """
        with open(abs_path_syncTokenGroups, "w+") as file :
            file.writelines([token+"\n",str(datetime.datetime.now())])

    def fetch_all(self) :
        """
        Args : None
        Return : fetched contacts, groups, email and if chosen, other contacts for chosen email (type -> list)
        Main function for syncing contacts, groups and other contacts. Transforms the fetched 2D lists into flat lists and returns them (+ email account for which the sync was done)
        """
        Logger(0)

        contacts = list(itertools.chain.from_iterable(self.fetch_contacts())) ## making it flat
        groups = list(itertools.chain.from_iterable(self.fetch_groups())) ## making it flat
        other_contacts = []
        if syncOtherContacts :
            other_contacts = list(itertools.chain.from_iterable(self.fetch_other_contacts()))

        Logger(2,str(len(contacts)) + '/' + str(len(groups)) + '/' + str(len(other_contacts)))

        return contacts, groups, account_email, other_contacts

    def list_all_other_contacts(self, **kwargs):
        """
        Args : **kwargs, any keyworded parameters to fetch the api
        Return : All the other contacts fetched from the api (type -> dict)
        Makes a request to the server with the correct parameters, and returns a dict (json if needed to export)
        """
        try : 
            return self.service.otherContacts().list(**kwargs).execute()
        except Exception as e :
            Logger(-1,e)
            print("There was an error while fetching other contacts")
            raise e
    def list_all_contacts(self, **kwargs) :
        """
        Args : **kwargs, any keyworded parameters to fetch the api
        Return : All the contacts fetched from the api (type -> dict)
        Makes a request to the server with the correct parameters, and returns a dict (json if needed to export)
        """
        try :
            return self.service.people().connections().list(**kwargs).execute()
        except Exception as e :
            Logger(-1,e)
            print("There was an error while fetching contacts")
            raise e
    def list_all_groups(self, **kwargs) :
        """
        Args : **kwargs, any keyworded parameters to fetch the api
        Return : All the groups fetched from the api (type -> dict)
        Makes a request to the server with the correct parameters, and returns a dict (json if needed to export)
        """
        try :
            return self.service.contactGroups().list(**kwargs).execute()
        except Exception as e :
            Logger(-1,e)
            print("There was an error while fetching groups")
            raise e
        
    def fetch_groups(self):
        """
        Args : None
        Return : self.groups - either empty, or list with groups
        First, the function verifies if a syncToken is available . 
        If not, it checks if it was stored in the syncToken.py file, if yes, reads it from there only if the time difference is not too big (maxSyncHours) and ignoreSyncTokens is False
        Next, depending on it's availability, it calls the list_all_groups function with the right parameters (with sync Token, or not).
        Possible cases :
            - if a lot of requests are to be made (a lot of groups to get, and 1 request with it's pageSize is not big enough), then does a new request with the previous nextPageToken
            - if no updates were made since the last query (only possible with syncToken), then it stops and returns an empty list ('contactGroups' not in json)
            - last case, it just received the last package
        When any of these finishes, it saves the received syncToken, and returns groups.
        """
        print("Getting groups...")
        if not self.syncTokenGroups and not ignoreSyncTokens:
            with open(abs_path_syncTokenGroups,'r+') as file :
                lines = file.readlines()
                if len(lines) == 2 :
                    time_delta = (datetime.datetime.now() - datetime.datetime.strptime(lines[1], '%Y-%m-%d %H:%M:%S.%f'))
                    if lines[0] and time_delta.total_seconds()/3600 < maxSyncHours:
                        self.syncTokenGroups = lines[0].strip()
                    else :
                        pass
                else : 
                    pass

        all_group_packets_received, nextPageToken = False, False
        self.groups = []

        while not all_group_packets_received :
            
            try :
                try :
                    packet = self.list_all_groups(pageSize=1000, syncToken=self.syncTokenGroups if self.syncTokenGroups else None, pageToken = nextPageToken if nextPageToken else None)
                except :
                    packet= self.list_all_groups(pageSize=1000, pageToken = nextPageToken if nextPageToken else None)
                if "nextPageToken" in packet.keys():
                    nextPageToken=packet['nextPageToken']
                    self.groups.append(packet['contactGroups'])
                else :
                    if "contactGroups" not in packet.keys():
                        Logger(1, 'groups')
                        print("No groups were modified since the last call")
                        self.groups = []
                        self.syncTokenGroups = packet["nextSyncToken"]
                        self.save_syncToken_groups(self.syncTokenGroups)
                        all_group_packets_received = True
                        return self.groups
                    else :
                        try :
                            Logger(1, 'groups')
                            self.groups.append(packet['contactGroups'])
                            self.syncTokenGroups = packet["nextSyncToken"]
                            self.save_syncToken_groups(self.syncTokenGroups)
                            all_group_packets_received = True
                            groups_final = self.groups
                            print("All groups received !")
                            return groups_final
                        except Exception as e:
                            print("Error while saving groups")
                            Logger(-1,e)
                            raise e
                        
            except Exception as e :
                Logger(-1, e)
                print("There was an error while getting groups")
                raise e
    def fetch_contacts(self) :
        """
        Args : None
        Return : self.contacts - either empty, or list with contacts
        First, the function verifies if a syncToken is available . 
        If not, it checks if it was stored in the syncToken.py file, if yes, reads it from there only if the time difference is not too big (maxSyncHours) and ignoreSyncTokens is False
        Next, depending on it's availability, it calls the list_all_contacts function with the right parameters (with sync Token, or not).
        Possible cases :
            - if a lot of requests are to be made (a lot of contacts to get, and 1 request with it's pageSize is not big enough), then does a new request with the previous nextPageToken
            - if no updates were made since the last query (only possible with syncToken), then it stops and returns an empty list ('connections' not in json)
            - last case, it just received the last package
        When any of these finishes, it saves the received syncToken, and returns contacts.
        """
        print("Getting contacts...")
        if not self.syncTokenContacts and not ignoreSyncTokens :
            with open(abs_path_syncTokenContacts,'r+') as file :
                lines = file.readlines()
                if len(lines) == 2 :
                    time_delta = (datetime.datetime.now() - datetime.datetime.strptime(lines[1], '%Y-%m-%d %H:%M:%S.%f'))
                    if lines[0] and time_delta.total_seconds()/3600 < maxSyncHours:
                        self.syncTokenContacts = lines[0].strip()
                    else :
                        pass
                else : 
                    pass
        all_packets_received, nextPageToken = False, False
        self.contacts = []

            
        while not all_packets_received :

            try :
                try :
                    packet = self.list_all_contacts(resourceName="people/me", personFields=PERSON_FIELDS, requestSyncToken=True, syncToken=self.syncTokenContacts if self.syncTokenContacts else None, pageToken = nextPageToken if nextPageToken else None,
                    pageSize=1000)
                except :
                    packet = self.list_all_contacts(resourceName="people/me", personFields=PERSON_FIELDS, requestSyncToken=True, pageToken = nextPageToken if nextPageToken else None,
                    pageSize=1000)
                if "nextPageToken" in packet.keys():
                    nextPageToken=packet['nextPageToken']
                    self.contacts.append(packet['connections'])
                else :
                    if "connections" not in packet.keys():
                        Logger(1, 'contacts')
                        print("No contacts were modified since the last call")
                        self.syncTokenContacts = packet["nextSyncToken"]
                        self.save_syncToken_contacts(self.syncTokenContacts)
                        all_packets_received = True
                        return self.contacts
                    else :
                        try :
                            Logger(1, 'contacts')
                            self.contacts.append(packet['connections'])
                            self.syncTokenContacts = packet["nextSyncToken"]
                            self.save_syncToken_contacts(self.syncTokenContacts)
                            all_packets_received = True
                            contacts_final = self.contacts
                            print("All contacts received !")
                            return contacts_final
                        except Exception as e:
                            print("Error while saving contacts")
                            Logger(-1,e)
                            raise e
                        
            except Exception as e :
                Logger(-1, e)
                print("There was an error while getting contacts")
                raise e
    def fetch_other_contacts(self):
        """
        Args : None
        Return : self.other_contacts - either empty, or list with other contacts
        First, the function verifies if a syncToken is available. 
        If not, it checks if it was stored in the syncToken.py file, if yes, reads it from there only if the time difference is not too big (maxSyncHours) and ignoreSyncTokens is False
        Next, depending on it's availability, it calls the list_all_other_contacts function with the right parameters (with sync Token, or not).
        Possible cases :
            - if a lot of requests are to be made (a lot of other contacts to get, and 1 request with it's pageSize is not big enough), then does a new request with the previous nextPageToken
            - if no updates were made since the last query (only possible with syncToken), then it stops and returns an empty list ('connections' not in json)
            - last case, it just received the last package
        When any of these finishes, it saves the received syncToken, and returns other contacts.
        """

        print("Getting other contacts...")
        if not self.syncTokenOtherContacts and not ignoreSyncTokens :
            with open(abs_path_syncTokenOtherContacts,'r+') as file :
                lines = file.readlines()
                if len(lines) == 2 :
                    time_delta = (datetime.datetime.now() - datetime.datetime.strptime(lines[1], '%Y-%m-%d %H:%M:%S.%f'))
                    if lines[0] and time_delta.total_seconds()/3600 < maxSyncHours:
                        self.syncTokenOtherContacts = lines[0].strip()
                    else :
                        pass
                else : 
                    pass
                
        all_packets_received, nextPageToken = False, False
        self.other_contacts = []

            
        while not all_packets_received :

            try :
                try :
                    packet = self.list_all_other_contacts(readMask=READ_MASK, requestSyncToken=True, syncToken=self.syncTokenOtherContacts if self.syncTokenOtherContacts else None, pageToken = nextPageToken if nextPageToken else None,
                    pageSize=1000)
                except :
                    packet = self.list_all_other_contacts(readMask=READ_MASK, requestSyncToken=True, pageToken = nextPageToken if nextPageToken else None,
                    pageSize=1000)
                if "nextPageToken" in packet.keys():
                    nextPageToken=packet['nextPageToken']
                    self.other_contacts.append(packet['otherContacts'])
                else :
                    if "otherContacts" not in packet.keys():
                        Logger(1, 'other contacts')
                        print("No other contacts were modified since the last call")
                        self.syncTokenOtherContacts = packet["nextSyncToken"]
                        self.save_syncToken_other_contacts(self.syncTokenOtherContacts)
                        all_packets_received = True
                        return self.other_contacts
                    else :
                        try :
                            Logger(1, 'other contacts')
                            self.other_contacts.append(packet['otherContacts'])
                            self.syncTokenOtherContacts = packet["nextSyncToken"]
                            self.save_syncToken_other_contacts(self.syncTokenOtherContacts)
                            all_packets_received = True
                            other_contacts_final = self.other_contacts
                            print("All other contacts received !")
                            return other_contacts_final
                        except Exception as e:
                            print("Error while saving other contacts")
                            Logger(-1,e)
                            raise e
                        
            except Exception as e :
                Logger(-1, e)
                print("There was an error while getting other contacts")
                raise e    
    

