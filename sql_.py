import logging
import pymysql
import scrap_ as sc
from main_ import password


logger = logging.getLogger(__name__)
format_logger = '[%(asctime)s line %(lineno)d] %(message)s'
logging.basicConfig(filename='apptrace.log', level=logging.INFO, format=format_logger)
stream_handler = logging.StreamHandler()


# def password():
#     sql_password = input('Please insert your mysql password:' + '\n')
#     return sql_password


def connect_sql(sql_password):
    conn = pymysql.connect(host='localhost', user='root', passwd=sql_password)
    mycursor = conn.cursor()
    return mycursor


def create_database(sql_password, database_name):
    mycursor = connect_sql(sql_password)
    mycursor.execute("DROP DATABASE IF EXISTS apptrace")
    mycursor.execute("CREATE DATABASE apptrace")

    conn = pymysql.connect(host='localhost', user='root', passwd=sql_password, database=database_name)
    mycursor = conn.cursor()

    # dev table
    mycursor.execute("CREATE TABLE dev("
                     "id INT PRIMARY KEY,"
                     "name VARCHAR(255),"
                     "ios_app_num INT,"
                     "ranking INT)")
    # app table
    mycursor.execute("CREATE TABLE app ("
                     "id INT PRIMARY KEY,"
                     "name VARCHAR(255),"
                     "price DOUBLE, "
                     "curr_rating DOUBLE, "
                     "curr_num_ratings INT, "
                     "age DOUBLE,"
                     "available_in INT,"
                     "activity INT,"
                     "overall_num_ratings INT, "
                     "global_rank INT, "
                     "top_25_overall INT,"
                     "avg_rating DOUBLE,"
                     "total_versions INT,"
                     "top_1 INT,"
                     "top_10 INT,"
                     "top_50 INT,"
                     "top_100 INT,"
                     "top_300 INT,"
                     "dev_id INT,"
                     "tweet_score INT,"
                     "tweets_time_for_50 INT,"
                     "FOREIGN KEY (dev_id) REFERENCES dev(id) )")

    # country
    mycursor.execute("CREATE TABLE country ("
                     "id INT PRIMARY KEY, "
                     "country VARCHAR(255))")

    # table app_country_rank
    mycursor.execute("CREATE TABLE app_country_rank ("
                     "id INT PRIMARY KEY AUTO_INCREMENT,"
                     "app_id INT,"
                     "country_id INT,"
                     "ranking INT,"
                     "FOREIGN KEY (app_id) REFERENCES app(id),"
                     "FOREIGN KEY (country_id) REFERENCES country(id),"
                     "UNIQUE (app_id, country_id))")
    # table category
    mycursor.execute("CREATE TABLE category ("
                     "id INT PRIMARY KEY, "
                     "category VARCHAR(255))")
    # table app_category
    mycursor.execute("CREATE TABLE app_category ("
                     "app_id INT,"
                     "category_id INT,"
                     "FOREIGN KEY (app_id) REFERENCES app(id), "
                     "FOREIGN KEY (category_id) REFERENCES category(id) )")


def transform_to_digit_only(app_table):
    """
    a function to modify the app table element in order to fit our data
    :param app_table: some data of the app
    :return: the data in require form for the db
    """
    if 'year' in app_table[0]:
        app_table[0] = int(app_table[0].split('y')[0].rstrip())
    elif 'month' in app_table[0]:
        app_table[0] = round(int(app_table[0].split('m')[0].rstrip()) / 12, 2)
    elif 'day' in app_table[0]:
        app_table[0] = round(int(app_table[0].split('d')[0].rstrip()) / 365, 4)
    else:
        app_table[0] = -1
    app_table[1] = int(app_table[1].split('C')[0].rstrip())
    app_table[6] = int(app_table[6].split('C')[0].rstrip())
    try:
        app_table[5] = int(app_table[5][1:])
    except ValueError:
        app_table[5] = -1
    app_table[2] = int(app_table[2])
    try:
        app_table[3] = int(''.join(app_table[3].split()))
    except ValueError:
        app_table[3] = -1
    return app_table


def insert_in_db(list_, query):
    """
    The function perform insertion to the apptrace database according to the query and the list to insert
    :param list_: the list of value we want to insert in the current row
    :param query: the sql query
    """
    try:
        conn = pymysql.connect(host='localhost', user='root', passwd=password, database='apptrace')
        mycursor = conn.cursor()
        if type(list_) == list:
            mycursor.execute(query, tuple(list_))
        else:
            mycursor.execute(query, list_)
        conn.commit()
        # print(mycursor.rowcount, "was inserted.")
    except Exception as e:
        logger.exception(e)
    finally:
        mycursor.close()
        conn.close()


def data_exist(query, id):
    """
     the function checks if a certain id already exist in a table,
    :param query: sql query to perform the verification
    :param id: id of the row we want to check if already exist or not
    :return: True if the id exist already, False otherwise
    """
    conn = pymysql.connect(host='localhost', user='root', passwd=password, database='apptrace')
    mycursor = conn.cursor()
    mycursor.execute(query, (id,))
    data = "error"
    for i in mycursor:
        data = i
    if data == "error":
        return False
    else:
        return True


def insert_data_app(id_tag, dictionary_categories, dictionary_countries, driver):
    """
    The function insert the data of the application into the database
    :param id_tag: the app id
    :param dictionary_categories: the dictionary of the categories(key:id, value:categorie name)
    :param dictionary_countries: the dictionary of the countries (key: country name , value: code internet country
    :param driver:
    """
    try:
        if not data_exist("SELECT * FROM app WHERE id=%s", id_tag):
            query = "INSERT INTO app(id, name, price, curr_rating,curr_num_ratings, age, available_in, activity, overall_num_ratings,avg_rating, global_rank, top_25_overall, total_versions,dev_id, top_1,top_10,top_50,top_100,top_300, tweet_score, tweets_time_for_50) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            list_info = sc.get_data_by_id(id_tag)
            insert_in_db(list_info + sc.get_top_rankings(id_tag, driver) + sc.twitter_info(id_tag), query)
            # print((list_info[1]) + ' : row inserted in app table')
            sc.get_categories(id_tag, dictionary_categories)
            sc.rankings_countries(id_tag, driver, ['top_countries', 'world'], dictionary_countries)
            logger.info(str(id_tag) + ': row inserted in app_country_rank table \n')
        else:
            logger.info('app already in database \n')
    except Exception as e:
        logger.exception(e)
