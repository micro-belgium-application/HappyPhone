import datetime
from os.path import dirname as dir
import os

logs_path = (dir(dir(dir(__file__))) + '/logs/').replace('\\', '/')
errors_path = (dir(dir(dir(__file__))) + '/errors/').replace('\\', '/')
class Logger :

    def __init__(self, code, message=None):
        """
        Args : code (type -> int), message with default argument None (type -> any)
        Return : None
        Constructor for logger class, converts, if there is any, the message to str, deletes old log files and writes to log files  
        """
        self.message = str(message)
        self.code = code
        #self.delete_old_logs()
        self.write_to_file()
    def delete_old_logs(self):
        """
        Args : None
        Return : None
        Deletes log files that are too old (> 14 days)
        """
        for filename in os.listdir(logs_path) :
            try : 
                time_delta = datetime.datetime.now().date() - datetime.datetime.strptime(filename, '%Y-%m-%d').date()
                if  time_delta.days > 14 :
                    os.remove(logs_path + filename)
                else :
                    pass
            except Exception as e: 
                print('Error while deleting files')
                raise e
                
                    
    def write_to_file(self):
        """
        Args : None
        Return : None
        Main function that writes to the right file, depending on the date. The self.code property also influences what the function writes :
        Code guide :
        - -1 -> Error somewhere 
        - 0 -> Launch of a new routine
        - 1 -> Fetched the API 
        - 2 -> Informing us about the number of contacts modified
        - 3 -> Informing us about the cleaning of contacts
        - 4 -> Informing us about the database location and state of push 
        - 5 -> Visual separation between records 
        - 6 -> Printing email account for fetch 
        - 7 -> Quantity of contacts without a name
        """
        today = datetime.datetime.now().date()
        with open(logs_path + str(today) + '.txt', 'a+') as file:
            if self.code == -1 :
                file.writelines([self.message, '\n'])
                with open(errors_path + str(today) + '.error', 'a+') as file_error:
                    file_error.writelines([self.message, '\n'])
            if self.code == 0 :
                file.writelines(["Log time : ", str(datetime.datetime.now()),'\n'])
            if self.code == 1 :
                file.writelines(["Fetched the API successfully for ", self.message, '\n'])
            if self.code == 2 :
                file.writelines(["Contacts/Groups/other Contacts modified : ", self.message, '\n'])
            if self.code == 3 :
                file.writelines([self.message, " successfully cleaned", '\n'])
            if self.code == 4 :
                file.writelines(["Contacts pushed successfully to : ", self.message, '\n' ])
            if self.code == 5 :
                file.writelines(["#########################\n",])
            if self.code == 6 :
                file.writelines(["Email account : ", self.message, '\n'])
            if self.code == 7 :
                file.writelines(["Number of unnamed contacts : ", self.message, '\n'])

    