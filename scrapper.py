import requests
from bs4 import BeautifulSoup
import datetime
from selenium.webdriver import Chrome


def get_date_apptrace():
    """
    :return: the date of today for our url
    """
    date = str(datetime.datetime.today()).split()[0]
    list_date = date.split('-')
    list_url = []
    for i in list_date:
        list_url.append(i.lstrip('0'))
    date_url = '-'.join(list_url)
    return date_url


def get_data_by_id(id):
    """
    :param id_set:
    :return: the data of every application according to the id
    """
    try:
        page = requests.get('https://www.apptrace.com/app/' + str(id)).text
        soup = BeautifulSoup(page, 'lxml')
        app_detail = soup.find('div', class_='app_details')
        name = soup.find('li', class_='apptitle').h1.text
        developer = soup.find('li', class_='apptitle').h2.a.span.text
        #create new dictinnary with all the data of the applciation
        dic = {}
        dic['Name app'] = name
        dic['Developer'] = developer
        dic['Price'] = soup.find('li', class_='apptype appstore').text
        for detail in app_detail.find_all('div', class_='infobox'):
            dic[(detail.find('p', class_='title').text)] = (detail.find('p', class_='data').text)
        row_rating = app_detail.find('div', class_='row rating')
        dic['Rating'] = row_rating.find('strong', itemprop='ratingValue').text + "/5"
        dic['Ratings Count'] = row_rating.find('span', itemprop='ratingCount').text
        dic['Description'] = app_detail.find('div', class_='t1c active_language').text
        count = 0
        for detail in soup.find('div', class_='table versions opened').find_all('div', class_="cell"):
            #print(detail.text)
            count += 1
        dic['Number of versions'] = int(count / 2)

        #print the dictionnary
        for k, v in dic.items():
            print(k, ":", v)
    except Exception as e:
        print(e)


def get_ranks_by_id(id):
    dict_infos = {}
    driver = Chrome()
    page = requests.get("https://www.apptrace.com/app/" + str(id) + "/ranks")
    soup = BeautifulSoup(page.content, 'lxml')

    driver.get("https://www.apptrace.com/app/" + str(id) + "/ranks")

    for i, cat in enumerate(soup.find_all('a', class_='genre_selector')):
        if cat.text != 'Overall':
            dict_infos['Category #' + str(i)] = cat.text

    rankings = driver.find_elements_by_class_name("infobox")
    for ranking in rankings:
        ranking_title = ranking.find_element_by_class_name("title").text
        ranking_rank = ranking.find_element_by_class_name("data").text
        dict_infos[ranking_title] = "#" + ranking_rank

    try:
        rank_top_countries = driver.find_element_by_id("rankings_by_genre_top_countries")
        top_countries = rank_top_countries.find_elements_by_class_name("cell")
        for country in top_countries:
            country_name = country.find_element_by_class_name("content").text
            country_rank = country.find_element_by_class_name("rank").text
            dict_infos[country_name + ' Ranking'] = "#" + country_rank
    except Exception:
        print("No ranking in top countries")

    try:
        rank_other_countries = driver.find_element_by_id("rankings_by_genre_world")
        other_countries = rank_other_countries.find_elements_by_class_name("cell")
        for country in other_countries:
            country_name = country.find_element_by_class_name("content").text
            country_rank = country.find_element_by_class_name("rank").text
            dict_infos[country_name + ' Ranking'] = "#" + country_rank
    except Exception:
        print("No ranking in other countries")

    for key in dict_infos:
        print(key, ':', dict_infos[key])

    driver.close()


# create a new set of id of application so we won't get any deplicates
id_app_set = {1031002863}


def get_app_id_by_category_by_country(dictionary_countries,dictionary_categories):
    """
    :param dictionary_countries: the dictionarry of key = country and value = code internet - data-link
    :param dictionary_categories: the dictionary of keys = data-link of every category ,  the values = categories name
    :return:
    """
    paid_or_free = ['free', 'paid']
    for cost in paid_or_free:
        for key in dictionary_categories.keys():
            for country in dictionary_countries.keys():
                try:
                    page = requests.get('https://www.apptrace.com/Itunes/charts/' + dictionary_countries[country] + '/top' + cost + 'applications/' + str(key) + '/2020-3-9').text
                    soup = BeautifulSoup(page, 'lxml')
                    for tag in soup.find_all('div', class_ ='cell linked app_cell'):
                        id_tag = int(tag.find('div', class_='id').get('id'))
                        if id_tag not in id_app_set:
                            id_app_set.add(id_tag)
                            print("Scrapped for the first time in: " + country + "/" + dictionary_categories[key]+ "/" + cost)
                            get_data_by_id(id_tag)
                            get_ranks_by_id(id_tag)
                            print()
                            print(len(id_app_set))
                except Exception as e:
                       print(e)


def get_country_dic():
    """
    :return: a dictionary of all the countries we want to scrap application data.
    keys are countries and values are the data link : code internet of the country (ex: il)
    """
    url = requests.get('https://www.apptrace.com/charts')
    country_chart_page = BeautifulSoup(url.content, 'lxml').find('ul', class_='countryselect')
    dict_country = {}
    for country in country_chart_page.find_all('li', class_='visible'):
        dict_country[country.text] = country.a.get('data-link')
    for country in country_chart_page.find_all('li', class_='invisible'):
        dict_country[country.text] = country.a.get('data-link')
    return dict_country


def get_category_dic():
    """
    :return: a dictionary : keys are the data-link of every category and the values are the categories name
    """
    url = requests.get('https://www.apptrace.com/charts')
    country_chart_page = BeautifulSoup(url.content, 'lxml')
    dic_category = {}
    for selector in country_chart_page.find_all('a', class_='genre_selector'):
        dic_category[selector.get('data-link')] = selector.text
        if selector.text == 'Weather':
            break
    # delete all the sub-categories of magazines and newspapers because there is not data there
    list_to_delete = list(range(31, 49)) + list(range(11, 20)) + [54]
    for num in list_to_delete:
        del dic_category[str(num)]
    return dic_category


def main():
    dictionary_countries = get_country_dic()
    dictionary_categories = get_category_dic()
    get_app_id_by_category_by_country(dictionary_countries, dictionary_categories)


if __name__ == "__main__":
    main()

