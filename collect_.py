import logging
import sql_ as sq
import scrap_ as sc


logger = logging.getLogger(__name__)
format_logger = '[%(asctime)s line %(lineno)d] %(message)s'
logging.basicConfig(filename='apptrace.log', level=logging.INFO, format=format_logger)
stream_handler = logging.StreamHandler()


def get_country_dic():
    """
    The function create a dictionary of all the countries we want to scrap app data from
    :return: a dictionary where keys are name of the countries and values are the data link : code internet of the country (ex: il)
    """
    country_chart_page = sc.get_soup('https://www.apptrace.com/charts').find('ul', class_='countryselect')
    dict_country = {}
    list_country = []
    sample_id = 1
    query = "INSERT INTO country(id, country) VALUES (%s,%s)"
    for country in country_chart_page.find_all('li', class_='invisible'):
        dict_country[country.text] = country.a.get('data-link')
        list_country.append(country.text)
        if not sq.data_exist("SELECT * FROM country WHERE id=%s", sample_id):
            sq.insert_in_db([sample_id, country.text], query)
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
    for selector in sc.get_soup('https://www.apptrace.com/charts').find_all('a', class_='genre_selector'):
        dic_category[selector.get('data-link')] = selector.text
        if selector.text == 'Weather':
            break
    # delete all the sub-categories of magazines and newspapers because there is no data there
    list_to_delete = list(range(31, 49)) + list(range(11, 20)) + [54]
    for num in list_to_delete:
        del dic_category[str(num)]
    return dic_category


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
                    soup = sc.get_soup('https://www.apptrace.com/Itunes/charts/' + dictionary_countries[country] + \
                                    '/top' + cost + 'applications/' + str(key) + '/' + sc.get_date_apptrace())
                    for tag in soup.find_all('div', class_='cell linked app_cell'):
                        id_tag = int(tag.find('div', class_='id').get('id'))
                        logger.info("Scrapping in: " + country + "/" + dictionary_categories[key] + "/" + cost)
                        driver.get("https://www.apptrace.com/app/" + str(id_tag) + "/ranks")
                        sq.insert_data_app(id_tag, dictionary_categories, dictionary_countries, driver)
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
            sq.insert_data_app(id_tag, dictionary_categories, dictionary_countries, driver)
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

