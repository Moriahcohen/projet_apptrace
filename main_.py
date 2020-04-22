from selenium.webdriver import Chrome
import logging
import argparse
import sql_ as sq
import collect_ as col
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger(__name__)
format_logger = '[%(asctime)s line %(lineno)d] %(message)s'
logging.basicConfig(filename='apptrace.log', level=logging.INFO, format=format_logger)
stream_handler = logging.StreamHandler()


# Defining parser
parser_scrap = argparse.ArgumentParser(description='Scrap app info')
parser_scrap.add_argument('-c', '--country', nargs='+', metavar='', type=str,
                          help='If you want to scrap apps from specific countries. Must be a string or strings')
parser_scrap.add_argument('-k', '--category', nargs='+', metavar='', type=str,
                          help='If you want to scrap apps from specific categories. Must be a string or strings')
parser_scrap.add_argument('-i', '--id', nargs='+', metavar='', type=int,
                          help='If you want to scrap apps with specific ids. Must be an integer or integers')

args = parser_scrap.parse_args()

password = ''


def main():
    global password
    # sq.create_database(password, 'apptrace')
    driver = webdriver.Firefox(executable_path='/Users/moriahzur/Downloads/geckodriver')
    #driver = Chrome('/Users/moriahzur/project1/projet_apptrace/chromedriver')
    dictionary_categories = col.get_category_dic()
    # insert into the table 'category' the id and the name of the categories
    query = "INSERT INTO category(id, category) VALUES (%s,%s)"
    for key, value in dictionary_categories.items():
        if not sq.data_exist("SELECT * FROM category WHERE id=%s", key):
            sq.insert_in_db([key, value], query)
    logger.info('all the categories inserted in category successfully')

    # start scrapping and inserting every app, dev, ranking data in our database
    if args.country and args.category:
        col.by_country(args.country, args.category, driver)
    elif args.country and not args.category:
        col.by_country(args.country, col.get_category_dic(), driver)
    elif not args.country and args.category:
        col.by_country(col.get_country_dic(), args.category, driver)
    elif args.id:
        col.by_id(driver, args.id, col.get_category_dic(), col.get_country_dic())
    else:
        col.get_app_id_by_category_by_country(col.get_country_dic(), col.get_category_dic(), driver)
    driver.close()


if __name__ == "__main__":
    main()
