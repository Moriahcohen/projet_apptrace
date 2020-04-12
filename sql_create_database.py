import pymysql

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

    #dev table
    mycursor.execute("CREATE TABLE dev("
                     "id INT PRIMARY KEY,"
                     "name VARCHAR(255),"
                     "ios_app_num INT,"
                     "ranking INT)")
    #app table
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
                     "FOREIGN KEY (dev_id) REFERENCES dev(id) )")

    #country
    mycursor.execute("CREATE TABLE country ("
                     "id INT PRIMARY KEY, "
                     "country VARCHAR(255))")

    #table app_country_rank
    mycursor.execute("CREATE TABLE app_country_rank ("
                     "id INT PRIMARY KEY AUTO_INCREMENT,"
                     "app_id INT,"
                     "country_id INT,"
                     "ranking INT,"
                     "FOREIGN KEY (app_id) REFERENCES app(id),"
                     "FOREIGN KEY (country_id) REFERENCES country(id),"
                     "UNIQUE (app_id, country_id))")
    #table category
    mycursor.execute("CREATE TABLE category ("
                     "id INT PRIMARY KEY, "
                     "category VARCHAR(255))")
    #table app_category
    mycursor.execute("CREATE TABLE app_category ("
                     "app_id INT,"
                     "category_id INT,"
                     "FOREIGN KEY (app_id) REFERENCES app(id), "
                     "FOREIGN KEY (category_id) REFERENCES category(id) )")

    # mycursor.execute("SHOW TABLES")
    # mycursor.execute("SHOW COLUMNS FROM app")
    # for db in mycursor:
    #     print(db)


def main():
    sql_password = input('please insert your sqlpassword ?' + '\n')
    create_database(sql_password,'apptrace')
    return sql_password


if __name__ == "__main__":
    main()
