# Prerequisites
- Install python 3.10
- Check that everything works properly
    ```
    python --version
    pip --version
	pip install virtualenv
    ```

# Installation
- Clone this repository : https://github.com/micro-belgium-application/HappyPhone
- Go inside the directory  
- Run `install.bat` to install the required python libraries
- Create a `config.yml` file on root folder and add the following content, then modify the parameters to connect to the database :
    ```
    account: 
        email: etienne.vancaillie@mba.be

    # Database settings, separated by ';' (PS : if any field has any ambiguous characters, for example ';' in pwd, surround it by '{' and '}' (between '=' and ';') )
    database_settings:
        database_connection:
                DRIVER={SQL Server};
                SERVER= {ADD SERVER NAME};
                DATABASE=GoogleContactsTest;
                UID= {ADD UID};
                PWD={ADD PSWD};
                Connect Timeout=60
        # for logs
        database : Server=.\SQLEXPRESS - GoogleContactsTest
    
    
    parameters:
        # True or False only   
        syncOtherContacts : True
        ignoreSyncTokens : True  
	writeUnnamedContactsIntoLogs : False
        # Time period (in hours) after which all contacts/groups/other contacts are fully synced again (if not modified during this time), integer
        maxSyncHours : 48
        # Time (in seconds) between every API fetch
        time_between_fetches : 120
    ```
- Add a `secrets` folder on the root and put inside the `client_secret.json` downloaded from [Google Console](https://console.cloud.google.com/) which contains the token to Google API.
- Create 3 python files, each containing the api token, in the following directory :
    - GoogleContactsSync/connection/syncTokenContacts.py
    - GoogleContactsSync/connection/syncTokenGroups.py
    - GoogleContactsSync/connection/syncTokenOtherContacts.py

# Launching 
- Run `boot.bat` to launch the routine

# Automatically launch at startup

- Create a shortcut of the boot.bat
- Open windows
- Type 'run' and enter 
- Type 'startup:...'
- Put the script boot.bat in the opened folder
