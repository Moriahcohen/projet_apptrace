import requests
from bs4 import BeautifulSoup
import datetime
from selenium.webdriver import Chrome
import logging

# clone our repository in github : https://github.com/Moriahcohen/projet_apptrace.git
# Moriah Cohen Scali and Roni Chauvart

logger = logging.getLogger(__name__)
logging.basicConfig(filename='apptrace.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
stream_handler = logging.StreamHandler()


def get_date_apptrace():
    """
    Format today's date to fit url format
    :return: the date of today for our url
    """
    date = str(datetime.datetime.today()).split()[0]
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


def get_data_by_id(id):
    """
    Build a dictionary with app data found on the main tab
    :param id_set:
    :return: the data of every application according to the id
    """
    try:
        soup = get_soup('https://www.apptrace.com/app/' + str(id))
        app_detail = soup.find('div', class_='app_details')
        url_dev = soup.find('li', class_='apptitle').h2.a.get('href')
        get_dev_info(url_dev)

        dic_app_details = {'Name app': soup.find('li', class_='apptitle').h1.text,
                           'Developer': soup.find('li', class_='apptitle').h2.a.text,
                           'Price': soup.find('li', class_='apptype appstore').text}
        for detail in app_detail.find_all('div', class_='infobox'):
            dic_app_details[detail.find('p', class_='title').text] = detail.find('p', class_='data').text
        row_rating = app_detail.find('div', class_='row rating')
        dic_app_details['Rating'] = row_rating.find('strong', itemprop='ratingValue').text + "/5"
        dic_app_details['Ratings Count'] = row_rating.find('span', itemprop='ratingCount').text
        dic_app_details['Description'] = app_detail.find('div', class_='t1c active_language').text
        dic_app_details['Number of versions'] = int(len(soup.find('div', class_='table versions opened').find_all('div', class_="cell"))/2)

        logger.info('Data main tab ok')
        return dic_app_details
    except Exception as e:
        logger.error(e)


def get_categories(id):
    """
    Get app categories
    :param id: url id of the app
    :return: dictionary with the app categories
    """
    try:
        dict_cat = {}
        for i, cat in enumerate(get_soup("https://www.apptrace.com/app/" + str(id) + "/ranks").find_all('a', class_='genre_selector')):
            if cat.text != 'Overall':
                dict_cat['Category #' + str(i)] = cat.text
        logger.info('Categories ok')
        return dict_cat
    except Exception as e:
        logger.error(e)


def get_top_rankings(id, driver):
    """
    Get app rankings in top 1/10/50/100/300
    :param id: url id of the app
    :param driver: usually Chrome
    :return: dictionary of app rankings in top 1/10/50/100/300
    """
    try:
        dict_top_rankings = {}
        rankings = driver.find_elements_by_class_name("infobox")
        for ranking in rankings:
            ranking_title = ranking.find_element_by_class_name("title").text
            ranking_rank = ranking.find_element_by_class_name("data").text
            dict_top_rankings[ranking_title] = "#" + ranking_rank
        logger.info('Top rankings ok')
        return dict_top_rankings
    except Exception as e:
        logger.error(e)


def rankings_countries(id, driver, countries_type):
    """
    Get app countries rankings in top countries or rest of the world
    :param id: url id of the app
    :param driver: usually Chrome
    :param countries_type : "top_countries" or "world"
    :return: dictionary of app rankings in top countries or rest of the world
    """
    dict_countries = {}
    try:
        countries = driver.find_element_by_id("rankings_by_genre_" + countries_type).find_elements_by_class_name("cell")
        for country in countries:
            country_name = country.find_element_by_class_name("content").text
            country_rank = country.find_element_by_class_name("rank").text
            dict_countries[country_name + ' Ranking'] = "#" + country_rank
        logger.info(countries_type + 'rankings ok')
        return dict_countries
    except Exception:
        logger.error("No ranking in " + countries_type)


# create a new set of id of application so we won't get any duplicates
id_app_set = {1031002863}


def get_app_id_by_category_by_country(dictionary_countries, dictionary_categories, driver):
    """
    Get all app data for apps within countries and categories
    :param dictionary_countries: the dictionary of key = country and value = code internet - data-link
    :param dictionary_categories: the dictionary of keys = data-link of every category ,  the values = categories name
    :param driver: usually Chrome
    :return: data for all apps within countries of dictionary_countries and categories of dictionary_categories
    """
    paid_or_free = ['free', 'paid']
    for cost in paid_or_free:
        for key in dictionary_categories.keys():
            for country in dictionary_countries.keys():
                try:
                    soup = get_soup('https://www.apptrace.com/Itunes/charts/' + dictionary_countries[country] + '/top' + cost + 'applications/' + str(key) + '/2020-3-9')
                    for tag in soup.find_all('div', class_ ='cell linked app_cell'):
                        id_tag = int(tag.find('div', class_='id').get('id'))
                        if id_tag not in id_app_set:
                            id_app_set.add(id_tag)
                            logger.info("Scrapped in: " + country + "/" + dictionary_categories[key]+ "/" + cost)
                            get_data_by_id(id_tag)
                            get_categories(id_tag)
                            driver.get("https://www.apptrace.com/app/" + str(id_tag) + "/ranks")
                            get_top_rankings(id_tag, driver)
                            rankings_countries(id_tag, driver, 'top_countries')
                            rankings_countries(id_tag, driver, 'world')
                            logger.info("Apps scrapped: {}".format(len(id_app_set)))
                except Exception as e:
                       logging.info(e)


def get_country_dic():
    """
    Create a dictionary of all the countries we want to scrap app data from
    :return: a dictionary where keys are countries and values are the data link : code internet of the country (ex: il)
    """
    country_chart_page = get_soup('https://www.apptrace.com/charts').find('ul', class_='countryselect')
    dict_country = {}
    for country in country_chart_page.find_all('li', class_='visible'):
        dict_country[country.text] = country.a.get('data-link')
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


def get_dev_info(dev):
    """
    Get information about a developer
    :param dev: dev id used in url
    :return: developer's info
    """
    try:
        soup = get_soup('https://www.apptrace.com' + dev)
        dev_info = []
        for tag in soup.find('div', class_='app-database devs'):
            for i in soup.find_all('li', class_='apptype'):
                dev_info.append(i.span.text)
        # print('developer name: ' + soup.find('li', class_='apptitle').h1.text)
        # print('developer id: ' + dev.split('/')[2])
        # print('developer global rank: ' + dev_info[0])
        # print('developer  IOS apps number: ' + dev_info[1])
        logger.info('Dev info ok')
    except Exception as e:
        logger.error(e)


def main():
    driver = Chrome()
    dictionary_countries = get_country_dic()
    dictionary_categories = get_category_dic()
    get_app_id_by_category_by_country(dictionary_countries, dictionary_categories, driver)
    driver.close()


if __name__ == "__main__":
    main()

