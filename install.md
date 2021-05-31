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
- Edit the connection to the DB in the file /api/api.py
    ```
    # Change if needed the globals variables:
    #Serveur config
    HOST = "192.168.8.215" => YOU HAVE TO CHANGE THIS 
    PORT = 8000
    #Database config
    SERVER = "192.168.8.211\MBASQL" 
    DATABASE = "HAppyPHone" 
    USERNAME = "saHappy"
    PASSWORD = "sz2aX0IXvp44zUFcCiEyI+DjCrAoSfMb5mQwgdq5XQI="
    SQL = "EXEC [dbo].[HappyPhone_Global_Search_For_Phone_Display] @numPhone="

    ```

#Launching 

- Run boot.bat

#Automatically launch at startup

- Create a shortcut of the boot.bat
- Open windows
- Type 'run' and enter 
- Type 'startup:...'
- Put the script boot.bat in the opened folder