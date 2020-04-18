import requests
from bs4 import BeautifulSoup
import datetime
import logging
import sql_ as sq


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
        return sq.transform_to_digit_only(app_table)
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
                        sq.insert_in_db([int(id), int(key)], query)
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
                        sq.insert_in_db([id, country_id, country_rank], query)
            logger.info(str(id) + ':' + type_ + ' rankings ok')
        except Exception:
            logger.info("No ranking in " + type_)


def get_dev_info(dev_id):
    """
    The function scrapp and insert in the table dev : id | name | ios_app_num | ranking of every developer
    :param dev_id: dev id used in url
    """
    try:
        if not sq.data_exist("SELECT * FROM dev WHERE id=%s", dev_id):
            soup = get_soup('https://www.apptrace.com/developer/' + dev_id)
            dev_table = [int(dev_id), soup.find('li', class_='apptitle').h1.text]
            for tag in soup.find('div', class_='app-database devs'):
                for i in soup.find_all('li', class_='apptype'):
                    try:
                        dev_table.append(int(i.span.text))
                    except ValueError:
                        dev_table.append(-1)
                sq.insert_in_db(dev_table[:4], "INSERT INTO dev(id, name, ranking, ios_app_num) VALUES (%s, %s, %s, %s) ")
                try:
                    logger.info(str(dev_id) + ' row inserted in dev table')
                except Exception as e:
                    print(e)
        else:
            logger.info('Dev exist already')
        logger.info('Dev info ok')
    except Exception as e:
        logger.exception(e)
