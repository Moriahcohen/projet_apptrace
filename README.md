# projet_apptrace

Apptrace 
a project to scrapp the  https://www.apptrace.com/ website and save data in a database

Our Apptrace project is composed of tho .py files:

1. sql_create_database:
    
    a script that creates our database structure using pymysql 

2. scrapper.py 
    
    the file scraps the https://www.apptrace.com/ website, the code is scrapping all 
    applications in the country charts, in every country in every category (paid and free), 
    for every application we scrapp and then insert in our apptrace database 
    - data about the app itself : app table 
    - his developper : dev table + foreign key from the app table (dev_id)
    - ranking in every coutries of the app: app_country_rank table with foreign key from country table (country.id) and from app table (app.id)
    - categories of the app : app_category with foreign key from category table (category.id) and from app table (app.id)
    
    In addition we have wrapped up our web scraper to be able to call it with different arguments from the
    terminal as: 
    - scrapping apps from specific countries
    - scrapping apps from specific categories
    - scrapping apps with specific ids
    
    And we are saving all our prints to our logging file: apptrace.log.


Prerequisites
just run the requirement.txt file


Authors
Moriah Cohen Sali
Roni Chauvart
