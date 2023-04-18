from datetime import datetime, timezone

from ..logger.logger import Logger
import json

class Clean:

    def __init__(self, contacts: list, groups: list, email: str, other_contacts: list):
        """
        Args : contacts, groups, email and other contacts (type -> list)
        Return: None
        """
        self.contacts = contacts
        self.groups = groups
        self.email = email
        self.other_contacts = other_contacts
    def get_clean_data(self):
        """
        Args : None
        Return : cleaned contacts, groups and other contacts
        Main cleaning function which calls clean functions for each type of data 
        """
        return self.clean_contacts(self.contacts), self.clean_groups(self.groups), self.clean_contacts(self.other_contacts)
    
    def clean_groups(self, groups):
        """
        Args : groups (type -> list)
        Return : cleaned groups (type -> list)
        Cleaning function for groups
        Returns an array of all groups, each one being a tuple
        """
        if groups == []:
            return groups
        else :
            all_groups = []
            for group in groups :
                if 'metadata' in group.keys():
                    if 'deleted' in group.get('metadata'):
                        deleted = True
                    else :
                        deleted = False
                else :
                    deleted = False
                all_groups.append((group['resourceName'], self.email, group['name'], group['groupType'], self.correct_datetime(group.get("metadata").get("updateTime") if group.get("metadata") else None), datetime.now(), deleted))
            
            return all_groups

    def clean_contacts(self, contacts):
        """
        Args : contacts (or other_contacts) (type -> list)
        Return : cleaned contacts (or other contacts) (type -> Tuple (List, List))
        Cleaning function for contacts (or other contacts) 
        Returns a tuple of an array of all contacts (each element being a dict) and unnamed contacts 
        """
        if not contacts :
            return None 
        else :
            all_contacts = []
            unnamed_contacts = []

            for contact in contacts :
                dico = {}
                is_named = True
                
                dico['id'] = contact['resourceName']
                dico['etag'] = contact['etag']
                
                try:
                    dico['lastModified'] = self.to_local_timezone(contact["metadata"]["sources"][0]["updateTime"]) if "metadata" in contact.keys() else None
                except Exception as e:
                    print(f"There was an error while fetching the date {e}")
                    Logger(-1,e)
                    dico['lastModified'] = datetime.now()

                if "metadata" in contact.keys():
                    # dico['idGoogle'] = contact['metadata']['sources'][0]['id']
                    if "deleted" in contact.get('metadata'):
                        dico['deleted']= True
                    else :
                        dico['deleted'] = False
                else :
                    dico['deleted'] = False   

                dico['lastSync'] = datetime.now()
                
                # Gets the full name of the contact
                if ("names" in contact):
                    dico['fullname'] = contact['names'][0]['displayName'] if 'displayName' in contact['names'][0].keys() else None
                    
                    if dico['fullname'] :
                    
                        dico['name'] = contact['names'][0]['givenName'] if 'givenName' in contact['names'][0].keys() else None
                    
                        dico['lastname'] = contact['names'][0]['familyName'] if 'familyName' in contact['names'][0].keys() else None
                    else :
                        dico['name'], dico['lastname'] = None, None
                        is_named = False
                else:
                    dico['fullname'],dico['name'],dico['lastname'] = None, None, None
                    is_named = False
                
                
                # PhoneNumbersNEW is an array with more data, that will be added to the GPhoneNumbers table in MSSQL
                if contact.get('phoneNumbers'):
                
                    dico['phoneNumbers'] = [(i["value"] if 'value' in i.keys() else None, i["type"] if 'type' in i.keys() else None) for i in contact.get('phoneNumbers')] if 'phoneNumbers' in contact.keys() else None
                    # PhonNumbersNEW is an array containing : [rawPhone, canonicalForm, integerForm, bigIntegerForm, phoneType, idGoogle]
                    dico["phoneNumbersNEW"] = [
                        (
                            i["value"] if 'value' in i.keys() else None, 
                            i["canonicalForm"] if 'canonicalForm' in i.keys() else None, 
                            i["canonicalForm"].replace('+', '00') if 'canonicalForm' in i.keys() else None,
                            int(i["canonicalForm"].replace('+', '')) if 'canonicalForm' in i.keys() else None,
                            i["type"] if 'type' in i.keys() else None,
                            i['metadata']["source"]["id"] if 'metadata' in i.keys() else None
                        ) for i in contact.get('phoneNumbers')                                                
                    ] if 'phoneNumbers' in contact.keys() else None                   

                else:
                    dico['phoneNumbers'] = None
                    dico['phoneNumbersNEW'] = None


                if contact.get("memberships"):
                    dico['groups'] = [i.get("contactGroupMembership")["contactGroupResourceName"] for i in contact['memberships'] if i.get("contactGroupMembership") ]
                else :
                    dico['groups'] = None
                if contact.get("addresses"):
                    Addresses = []
                    for i in contact.get("addresses"):
                        Addresses.append((self.clean_address(i)))
                    dico['addresses'] = Addresses      
                else :
                    dico['addresses'] = None
                if contact.get('userDefined') :
                    dico['userDefined'] = [(i["key"] if 'key' in i.keys() else None, i["value"] if 'value' in i.keys() else None) for i in contact.get("userDefined")]
                else :
                    dico['userDefined'] = None 
                if contact.get("emailAddresses"):
                    dico['emails'] = [(i["value"] if 'value' in i.keys() else None,i["type"] if 'type' in i.keys() else None) for i in contact.get("emailAddresses")] if "emailAddresses" in contact.keys() else None
                else :
                    dico['emails'] = None
                if "biographies" in contact.keys() :
                    dico['about'] = contact["biographies"][0]["value"] if "value" in contact["biographies"][0]  else None
                else :
                    dico['about'] = None
                if "organizations" in contact.keys() :
                    if contact.get("organizations")[0].get("name") :
                        dico['company'] = contact["organizations"][0]["name"] if "organizations" in contact.keys() else None
                    else :
                        dico['company'] = None
                    if contact.get("organizations")[0].get("title") :
                        dico['title'] = contact["organizations"][0]["title"] if "organizations" in contact.keys() else None 
                    else :
                        dico['title'] = None
                else :
                    dico['company'], dico['title'] = None, None
                dico['accountSrc'] = self.email
                dico['raw_json'] = json.dumps(contact)
                
                clean_json = {k: dico[k] for k in dico.keys() - {"lastSync", "lastModified", "metadata", "raw_json"}}
                dico['clean_json'] = json.dumps(clean_json)
                # Adds dico to all_contacts
                all_contacts.append(dico)

                # Adds dico to unnamed_contacts dic if the contact has no name
                if is_named == False:
                    unnamed_contacts.append(dico)

            Logger(3, "Contacts")
            
            return all_contacts, unnamed_contacts

    def correct_datetime(self, data):
        """
        Args: datetime (type -> str)
        Return : Either same str as input if correct format, or modifies it to correct format (type -> str)
        Some datetimes have a wrong format (too many decimals), which is not accepted by SQL, this is why we shorten it to 3 decimals for milliseconds 
        """
        if not data :
            return None
        else :
            if len(data) > 24 :
                data = data[:23] + 'Z'
                return data
            else :
                return data
    def to_local_timezone(self, string) :
        """
        Args : datetime in UTC (type -> string )
        Return : datetime in local time (type -> datetime.datetime)
        Conversion from UTC to local time
        """
        try : 
            return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
        except : 
            return datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
    def clean_address(self,address) :
        """
        Args : address (type -> dict)
        Return : tuple with either the right info, or None if not available in dict (type -> tuple)
        Cleans the address
        """
        return (address.get('type'),address.get('streetAddress'),address.get('city'),address.get('region'),address.get('postalCode'),address.get('country'),address.get("countryCode"))
