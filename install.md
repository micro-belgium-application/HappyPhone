#Prerequisites
- Install python3
- Check the everything works properly
    ```
    python --version
    pip --version
    ```

#Installation
- Clone this repository : https://github.com/exavince/HappyPhone.git
- Go inside the directory  
- Launch the script install.bat
- Edit the connection ot the DB in djangoPhone/settings.py
    ```
    # Change if needed :
    #   NAME wiht the name of the DB 
    #   HOST with the IP of the machine
    #   PORT with the port of the DB
  
    DATABASES = {
        'default': {
            'ENGINE': 'sql_server.pyodbc', 
            'NAME': 'HappyPhone', 
            'HOST': 'localhost', 
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'host_is_server': True,
                'Extra_Params':'Trusted_Connection=True'
            }
        }
    }
  
    # If you wan to use a dedicated user and password:
  
    DATABASES = {
        'default': {
            'ENGINE': 'sql_server.pyodbc', 
            'NAME': 'HappyPhone', 
            'HOST': 'localhost', 
            'USER': 'username',
            'PASSWORD': 'password',
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'host_is_server': True,
            }
        }
    }
    ```
- Edit ALLOWED_HOSTS in the file djangoPhone/settings.py
    ```
    #Replace the * with the IP of the machine
  
    ALLOWED_HOSTS = ['*.*.*.*','127.0.0.1',]
    ```
  
- Edit the script boot.bat with
    ```
    # Change the IP with the IP of the machine
  
    python manage.py runserver 192.168.1.216:8000
    ```

#Launching 

- Run boot.bat

#Automatically launch at startup

- Create a shortcut of the boot.bat
- Open windows
- Type 'run' and enter 
- Type 'startup:...'
- Put the script boot.bat in the opened folder