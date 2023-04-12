# HappyPhone
The HappyPhone application consists of communicating with the Google People API, and synchronize its data inside a Microsoft SQL Server.

## 1. Environment setup

Please follow the instructions on [install.md](install.md).

## 2. Architecture

### 2.1. Google API

The file `api_fetch.py` contains the `Connection` class. This class allows you to connect to the Google API and retrieve data from it. The application retrieves data from Contacts, Other Contacts, and Groups.

Starting from the second routine, the function will check if there have been any changes between the first routine and the current one, and return an empty list if no changes have been made to Google Contacts.

This part returns four lists of dictionaries to routine 4:
- contacts
- groups
- email
- other_contacts

### 2.2. Cleaning

Next, the data cleaning is done by the `cleaning_data` file and its `Clean` class. The application receives the four lists from the routine and creates three new lists that are prepared to be sent to the database.

Furthermore, the application checks if the contacts (and "other contacts") are registered with a name, and if the contact is improperly registered, it will be added to a separate list called `unnamed_contacts` in order to be recorded in a different log.

This part returns 3 elements in the following format:
- `cleaned_contacts`: Tuple(List(Dict)), where the first element of the tuple contains all the contacts and the second contains only those without a name (unnamed_contacts);
- `cleaned_groups`: List(Dict);
- `other_cleaned_cleaned`: Tuple(List(Dict)), where the first element of the tuple contains all the contacts and the second contains only those without a name (unnamed_contacts).

### 2.3. Logs

This part consists of logging the contacts that have been processed in text format. This is handled by the `log_contacts.py` file and its `LogContacts` class. The application takes as input the `cleaned_contacts` and `other_cleaned_cleaned` tuples, in order to join the nameless contacts into a single list, and then creates a new log in text format.

### 2.4. Database

Finally, the `export_to_sql` file and its SQL class retrieve the lists from the routine in order to send the data to the different tables of the `GoogleContacts` database.

The tables concerned are:

- GContactFeed
- GGroupContact
- GAddress
- GEmail
- GNumphone and GPhoneNumbers
- GUserDefined

## 3. References

## 4. Authors
- [Nicolas Samelson](https://github.com/nsamelson)