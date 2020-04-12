import requests
from bs4 import BeautifulSoup
import datetime
from selenium.webdriver import Chrome
import logging
import argparse
import pymysql
#import sql_create_database

# clone our repository in github : https://github.com/Moriahcohen/projet_apptrace.git
# Moriah Cohen Scali and Roni Chauvart

logger = logging.getLogger(__name__)
format_logger = '[%(asctime)s line %(lineno)d] %(message)s'
logging.basicConfig(filename='apptrace.log', level=logging.INFO, format=format_logger)
stream_handler = logging.StreamHandler()


def get_date_apptrace():
    """
    Format today's date to fit url format
    :return: the date of today for our url
    """
    date = str(datetime.datetime.today() - datetime.timedelta(days=2)).split()[0]
    list_date = date.split('-')
    list_url = []
    for i in list_date:
        list_url.append(i.lstrip('0'))
    date_url = '-'.join(list_url)
    return date_url


def get_soup(url):
    """Return a BeautifulSoup object given an url"""
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')
    return soup


def transform_to_digit_only(app_table):
    """
    a function to mmodify the app table element in ordor to fit our data
    :param app_table: some data of the app
    :return: the data in require form for the db
    """
    if 'year' in app_table[0]:
        app_table[0] = int(app_table[0].split('y')[0].rstrip())
    elif 'month' in app_table[0]:
        app_table[0] = round(int(app_table[0].split('m')[0].rstrip())/12, 2)
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
        conn = pymysql.connect(host='localhost', user='root', passwd=sql_password, database='apptrace')
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


def get_price(soup):
    """
    the function scrap and return the price of the app
    :param soup: soup of the app url
    :return: the price of the app
    """
    try:
        return soup.find('li', class_='apptype appstore').text[1:]
    except Exception as e:
        logger.exception(e)
        return -1


def get_name(soup):
    """
    the function scrap and return the name of the app
    :param soup: soup of the app url
    :return: the name of the app
    """
    try:
        return soup.find('li', class_='apptitle').h1.text
    except Exception as e:
        logger.exception(e)
        return 'nan'


def get_number_of_versions(soup):
    """
    the function scrap and return the number of versions of the app
    :param soup: soup of the app url
    :return: the number of version of the app
    """
    try:
        return int(len(soup.find('div', class_='table versions opened').find_all('div', class_="cell")) / 2)
    except Exception as e:
        logger.exception(e)
        return -1


def get_current_rating(soup):
    """
    the function scrap and return the rating of the current version of the app
    :param soup: soup of the app url
    :return: current rating of the app
    """
    try:
        app_detail = soup.find('div', class_='app_details')
        row_rating = app_detail.find('div', class_='row rating')
        current_rating = row_rating.find('strong', itemprop='ratingValue').text
    except AttributeError:
        logger.info('No current rating')
        current_rating = -1
    finally:
        return current_rating


def get_curr_num_rating(soup):
    """
    the function scrap and return the number of rating of the current version of the app
    :param soup: soup of the app url
    :return: the current number of ratings of the app
    """
    try:
        app_detail = soup.find('div', class_='app_details')
        row_rating = app_detail.find('div', class_='row rating')
        curr_num_rating = ''.join(row_rating.find('span', itemprop='ratingCount').text.split(' ')[:-1])
    except Exception as e:
        curr_num_rating = -1
    finally:
        return curr_num_rating


def get_app_table(soup):
    """
    the function scrap and return the data off the app_table of the app :
    --> [age, available_in, activity, overall_num_ratings, global_rank, top_25_overall, avg_rating]
    :param soup: soup of the app url
    :return: the app_table of the app
    """
    try:
        app_detail = soup.find('div', class_='app_details')
        app_table = []
        for i, detail in enumerate(app_detail.find_all('div', class_='infobox')):
            app_table.append(detail.find('p', class_='data').text)
            if i == 3:  # average_rating
                try:
                    app_table.append(float(detail.find('p', class_='info').text.split(' ')[-1]))
                except AttributeError:
                    logger.info('No average rating on overall')
                    app_table.append(-1)
        return transform_to_digit_only(app_table)
    except Exception as e:
        logger.exception(e)


def get_data_by_id(id):
    """
    the function scrapp and return the data of the app found on the main tab
    :param id_set:
    :return: the data of every application according to the id
    """
    try:
        soup = get_soup('https://www.apptrace.com/app/' + str(id))
        app_detail = soup.find('div', class_='app_details')
        dev_id = soup.find('li', class_='apptitle').h2.a.get('href').split('/')[2]
        get_dev_info(dev_id)
        name = get_name(soup)
        price = get_price(soup)
        app_table = get_app_table(soup)
        current_rating = get_current_rating(soup)
        curr_num_rating = get_curr_num_rating(soup)
        description = app_detail.find('div', class_='t1c active_language').text
        number_of_versions = get_number_of_versions(soup)
        list_info = [int(id), name, float(price), float(current_rating), int(curr_num_rating)] + app_table + [
            number_of_versions, int(dev_id)]
        logger.info(str(id) + ': Data from main tab ok')
        return list_info
    except Exception as e:
        logger.exception(e)


def get_categories(id, dictionary_categories):
    """
    the function scrapp the categories of the app and insert both foreign key in the table app_category
    :param id:  url id of the app
    :param dictionary_categories:  the dictionary of the categories ( key:id, value: category name)
    """
    try:
        query = "INSERT INTO app_category(app_id, category_id) VALUES (%s,%s)"
        for i, cat in enumerate(
                get_soup("https://www.apptrace.com/app/" + str(id) + "/ranks").find_all('a', class_='genre_selector')):
            if cat.text != 'Overall':
                for key, value in dictionary_categories.items():
                    if cat.text == value:
                        insert_in_db([int(id), int(key)], query)
                        logger.info(str(id) + '-' + str(value) + ':' + str(key) + ' inserted in app_category table successfully')
    except Exception as e:
        logger.exception(e)


def get_top_rankings(id, driver):
    """
    Get app rankings in top 1/10/50/100/300
    :param id: url id of the app
    :param driver: usually Chrome
    :return: a list of number of countries where the app in in top 1, top 10, top 50, top 100 and top 300
    """
    try:
        list_top_rankings = []
        rankings = driver.find_elements_by_class_name("infobox")
        for ranking in rankings:
            ranking_rank = ranking.find_element_by_class_name("data").text
            try:
                list_top_rankings.append(int(ranking_rank))
            except ValueError:
                list_top_rankings.append(0)
        logger.info('Top rankings ok')
        return list_top_rankings
    except Exception as e:
        logger.exception(e)


def rankings_countries(id, driver, list_type, dictionary_country):
    """
    the function scrapp and insert in the table app_country_rank the app countries rankings in the top countries
    and in the rest of the world
    :param id: url id of the app
    :param driver: usually Chrome
    :param list_type: "top_countries" or "world"
    :param dictionary_country: the dictionary of the countries
    """
    for type_ in list_type:
        try:
            countries = driver.find_element_by_id("rankings_by_genre_" + type_).find_elements_by_class_name("cell")
            for country in countries:
                country_name = country.find_element_by_class_name("content").text
                country_rank = country.find_element_by_class_name("rank").text
                query = "INSERT INTO app_country_rank (app_id, country_id, ranking) VALUES (%s,%s,%s)"
                country_id = 0
                for key in dictionary_country.keys():
                    country_id = country_id + 1
                    if key == country_name:
                        insert_in_db([id, country_id, country_rank], query)
            logger.info(str(id) + ':' + type_ + 'rankings ok')
        except Exception:
            logger.info("No ranking in " + type_)


def data_exist(query, id):
    """
     the function checks if a certain id already exist in a table,
    :param query: sql query to perform the verification
    :param id: id of the row we want to check if already exist or not
    :return: True if the id exist already, False otherwise
    """
    conn = pymysql.connect(host='localhost', user='root', passwd=sql_password, database='apptrace')
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
            query = "INSERT INTO app(id, name, price, curr_rating,curr_num_ratings, age, available_in, activity, overall_num_ratings,avg_rating, global_rank, top_25_overall, total_versions,dev_id, top_1,top_10,top_50,top_100,top_300) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            list_info = get_data_by_id(id_tag)
            insert_in_db(list_info + get_top_rankings(id_tag, driver), query)
            #print((list_info[1]) + ' : row inserted in app table')
            get_categories(id_tag, dictionary_categories)
            rankings_countries(id_tag, driver, ['top_countries', 'world'], dictionary_countries)
            logger.info(str(id_tag) + ': row inserted in app_country_rank table \n')
        else:
            logger.info('app already in database \n')
    except Exception as e:
        logger.exception(e)


def get_app_id_by_category_by_country(dictionary_countries, dictionary_categories, driver):
    """
    the function pass over all the app data by countries, by categories and by [free, paid]
    :param dictionary_countries: the dictionary of key = country and value = code internet - data-link
    :param dictionary_categories: the dictionary of keys = data-link of every category ,  the values = categories name
    :param driver: usually Chrome
    insert data for all apps within countries of dictionary_countries and categories of dictionary_categories
    """
    paid_or_free = ['free', 'paid']
    for country in dictionary_countries.keys():
        for key in dictionary_categories.keys():
            for cost in paid_or_free:
                try:
                    soup = get_soup('https://www.apptrace.com/Itunes/charts/' + dictionary_countries[country] + \
                                    '/top' + cost + 'applications/' + str(key) + '/' + get_date_apptrace())
                    for tag in soup.find_all('div', class_='cell linked app_cell'):
                        id_tag = int(tag.find('div', class_='id').get('id'))
                        logger.info("Scrapping in: " + country + "/" + dictionary_categories[key] + "/" + cost)
                        driver.get("https://www.apptrace.com/app/" + str(id_tag) + "/ranks")
                        insert_data_app(id_tag, dictionary_categories, dictionary_countries, driver)
                except Exception as e:
                    logger.exception(e)


def get_country_dic():
    """
    The function create a dictionary of all the countries we want to scrap app data from
    :return: a dictionary where keys are name of the countries and values are the data link : code internet of the country (ex: il)
    """
    country_chart_page = get_soup('https://www.apptrace.com/charts').find('ul', class_='countryselect')
    dict_country = {}
    list_country = []
    sample_id = 1
    query = "INSERT INTO country(id, country) VALUES (%s,%s)"
    for country in country_chart_page.find_all('li', class_='invisible'):
        dict_country[country.text] = country.a.get('data-link')
        list_country.append(country.text)
        if not data_exist("SELECT * FROM country WHERE id=%s", sample_id):
            insert_in_db([sample_id, country.text], query)
            sample_id = sample_id + 1
        else:
            logger.info(str(country.text) + ': country already in db')
    if sample_id == 156:
        logger.info('All countries in country dictionary')
    return dict_country


def get_category_dic():
    """
    Create a dictionary of all the categories we want to scrap app data from
    :return: a dictionary : keys are the data-link of every category and the values are the categories name
    """
    dic_category = {}
    for selector in get_soup('https://www.apptrace.com/charts').find_all('a', class_='genre_selector'):
        dic_category[selector.get('data-link')] = selector.text
        if selector.text == 'Weather':
            break
    # delete all the sub-categories of magazines and newspapers because there is no data there
    list_to_delete = list(range(31, 49)) + list(range(11, 20)) + [54]
    for num in list_to_delete:
        del dic_category[str(num)]
    return dic_category


def get_dev_info(dev_id):
    """
    The function scrapp and insert in the table dev : id | name | ios_app_num | ranking of every developer
    :param dev_id: dev id used in url
    """
    try:
        if not data_exist("SELECT * FROM dev WHERE id=%s", dev_id):
            soup = get_soup('https://www.apptrace.com/developer/' + dev_id)
            dev_table = [int(dev_id), soup.find('li', class_='apptitle').h1.text]
            for tag in soup.find('div', class_='app-database devs'):
                for i in soup.find_all('li', class_='apptype'):
                    try:
                        dev_table.append(int(i.span.text))
                    except ValueError:
                        dev_table.append(-1)
                insert_in_db(dev_table[:4], "INSERT INTO dev(id, name, ranking, ios_app_num) VALUES (%s, %s, %s, %s) ")
                try:
                    logger.info(str(dev_id) + ' row inserted in dev table')
                except Exception as e:
                    print(e)
        else:
            logger.info('Dev exist already')
        logger.info('Dev info ok')
    except Exception as e:
        logger.exception(e)


def by_id(driver, id_, dictionary_categories, dictionary_countries):
    """
    Get info for single/multiples specific app(s)
    :param dictionary_countries:
    :param dictionary_categories:
    :param driver: usually Chrome
    :param id_: an app id, or a list of ids
    :return: info for the app/apps
    """
    ids = [id_] if isinstance(id_, int) else id_
    for i, id_tag in enumerate(ids):
        try:
            driver.get("https://www.apptrace.com/app/" + str(id_tag) + "/ranks")
            insert_data_app(id_tag, dictionary_categories, dictionary_countries, driver)
            logger.info("{} apps scrapped \n".format(i + 1))
        except Exception as e:
            logger.exception(e)


def by_country(countries, cat, driver):
    """
    Get app info for single/multiple specific countries and categories
    :param countries: a country as a string or multiple countries in a list
    :param cat: a category as a string or multiple categories in a list
    :param driver: usually Chrome
    :return: App info for the specified countries and categories
    """
    try:
        list_countries = [countries] if isinstance(countries, str) else countries
        list_cat = [cat] if isinstance(cat, str) else cat
        all_cat_reverse = {value: key for key, value in get_category_dic().items()}
        dict_countries, dict_cat_reverse = {}, {}
        for country in list_countries:
            dict_countries[country] = get_country_dic()[country]
        for cat in list_cat:
            dict_cat_reverse[cat] = all_cat_reverse[cat]
        dict_cat = {value: key for key, value in dict_cat_reverse.items()}
        get_app_id_by_category_by_country(dict_countries, dict_cat, driver)
    except Exception as e:
        logger.exception(e)


# Defining parser
parser_scrap = argparse.ArgumentParser(description='Scrap app info')
parser_scrap.add_argument('-c', '--country', nargs='+', metavar='', type=str,
                          help='If you want to scrap apps from specific countries. Must be a string or strings')
parser_scrap.add_argument('-k', '--category', nargs='+', metavar='', type=str,
                          help='If you want to scrap apps from specific categories. Must be a string or strings')
parser_scrap.add_argument('-i', '--id', nargs='+', metavar='', type=int,
                          help='If you want to scrap apps with specific ids. Must be an integer or integers')

args = parser_scrap.parse_args()


def main():

    global sql_password
    sql_password = input('please insert your sqlpassword ?' + '\n')
    driver = Chrome()
    # dictionary_countries = get_country_dic()
    dictionary_categories = get_category_dic()
    # insert into the table 'category' the id and the name of the categories
    query = "INSERT INTO category(id, category) VALUES (%s,%s)"
    for key, value in dictionary_categories.items():
        if not data_exist("SELECT * FROM category WHERE id=%s", key):
            insert_in_db([key, value], query)
    logger.info('all the categories inserted in category successfuly')

    # start scrapping and inserting every app, dev, ranking data in our database
    if args.country and args.category:
        by_country(args.country, args.category, driver)
    elif args.country and not args.category:
        by_country(args.country, get_category_dic(), driver)
    elif not args.country and args.category:
        by_country(get_country_dic(), args.category, driver)
    elif args.id:
        by_id(driver, args.id, get_category_dic(), get_country_dic())
    else:
        get_app_id_by_category_by_country(get_country_dic(), get_category_dic(), driver)
    # get_app_id_by_category_by_country(dictionary_countries, dictionary_categories, driver)
    driver.close()


if __name__ == "__main__":
    main()
