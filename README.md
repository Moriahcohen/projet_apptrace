# projet_apptrace

Apptrace 
a project to scrapp the  https://www.apptrace.com/ website and save data in a database

Our Apptrace project is composed of the .py files:

1. sql_:
    A script that creates our database structure using pymysql when run.
    The script also includes all functions relevant data insertion into database.

2. scrap_.py
    This script includes all operations and functions needed to scrap the website

3. collect_.py
    This script includes all operations and functions needed to collect data.

4. api_twitter.py
    This script includes functions using Twitter API that will be used to enrich the database

5. main_.py
    The script to run.
    
And we are tracking operations in the logging file: apptrace.log.


////////// How does it work ? //////////
1. If you haven't already created the apptrace database in mySQL, you should do it first by running sql_.py
2. Run main_.py from your IDE or from the terminal where you can use option. 


Prerequisite:
Run the requirement.txt file


Authors
Moriah Cohen Sali
Roni Chauvart
