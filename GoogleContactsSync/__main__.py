from GoogleContactsSync import app
import argparse
import sys


"""
Author : Nicolas Samelson
Date : 04/04/2023
Summary : 

This is a sample to setup the python environment with all necessay libraries.

"""

# Configuration of argparse
parser = argparse.ArgumentParser(
    description="""This is the googlecontact application that synchronizes the contacts from google to SQL server""",
    epilog= """To run the program, please add necessary arguments"""
)
parser.add_argument("writeLogs", type=bool, help="Write logs of contacts in text format TYPE=BOOL")
args = parser.parse_args()

def main(writeLogs:bool=False):
    """
    Main function.
    """
    app.run(writeLogs)
if __name__ == '__main__' :
    n = list(sys.argv)
    main(n[1])
