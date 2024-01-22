from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import os
import glob
import pandas as pd
import datetime
import sqlite3

class g1b0024():
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        
        ## VARIABLES
        self.url = (r"""https://awti.3rdeyecam.com/tem/awti/login""")
        self.username = "username"
        self.password = "password"

        self.driver = webdriver.Firefox(options=options) # Remove args for non-headless
        self.driver.implicitly_wait(10)
        
        self.version_key = "g1b0024"
        self.css_path = ".gwt-SplitLayoutPanel > div:nth-child(4) > div:nth-child(1)\
                    > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)\
                    > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1)\
                    > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1)\
                    > tr:nth-child(1) > td:nth-child(7)"
        self.xpath1 = "/html/body/div[3]/div[2]/div/div[4]/div/div[3]/div/div[2]/div/div[4]\
                /table/tbody/tr/td/table/tbody/tr/td[9]/table/tbody/tr[2]/td/input"
        self.xpath2 = "/html/body/div[3]/div[2]/div/div[4]/div/div[3]/div/div[2]/div/div[5]\
                /div/div[3]/div/div[3]/div/div[2]/div/div/table/tbody/tr/td[1]/div\
                /input"
        self.xpath3 = "/html/body/div[3]/div[2]/div/div[4]/div/div[3]/div/div[2]/div/div[5]\
                /div/div[3]/div/div[3]/div/div[2]/div/div/table/tbody/tr/td[1]"
        self.xpath4 = "/html/body/div[3]/div[2]/div/div[4]/div/div[2]/table/tbody/tr/td[2]\
                /table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr/td[1]/div/div\
                /table/tbody/tr/td[1]"
        self.xpath5 = "/html/body/div[3]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]\
                /div/div/table/tbody/tr[1]/td/table/tbody/tr/td[7]/select/option[12]"
        self.xpath6 = "/html/body/div[3]/div[2]/div/div[4]/div/div[2]/table/tbody/tr/td[2]\
                /table/tbody/tr/td/table/tbody/tr/td[1]/table/tbody/tr/td[3]/div/div\
                /table/tbody/tr/td[1]"
        
        self.initialize_driver()
        print("Driver Initialized")
        self.navigate_to_breadcrumbs()
        print("Breadcrumbs Found")
        self.read_excel()
        print("Data Scraped")
        self.send_to_db()
        print("Data sent to Database")
        
    def initialize_driver(self):
        
        self.driver.get(self.url)
        # find username/email field and insert username
        self.driver.find_element("name", "j_username").send_keys(self.username)
        # find password input field and insert password
        self.driver.find_element("name", "j_password").send_keys(self.password)
        # click login button
        self.driver.find_element(By.CLASS_NAME, "buttonText").click()

        # wait the ready state to be complete
        WebDriverWait(driver=self.driver, timeout=10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )
        time.sleep(10)

    def navigate_to_breadcrumbs(self):

        self.driver.find_element("xpath", self.xpath1).send_keys(self.version_key) # input_num

        self.driver.find_element("xpath", self.xpath2).click() # checkbox1

        self.driver.find_element("xpath", self.xpath3).click() # checkbox1.5

        self.driver.find_element("xpath", self.xpath4).click() # show_btn

        duration_dropdown = self.driver.find_element("css selector", self.css_path)
        ActionChains(self.driver).move_to_element(duration_dropdown).click().perform() # For obscure clicking necessities

        self.driver.find_element("xpath", self.xpath5).click() # duration_selection 
        time.sleep(2)

        self.driver.find_element("xpath", self.xpath6).click() # download  
        
        time.sleep(3)
        self.driver.close()
        
    def read_excel(self):
        '''Index to Column mapping:
        index:  column:          cont.
          0      Time           |   8      Type
          1      Truck#         |   9      Descrition
          2      Driver         |   10     Pickup Distance(ft)
          3      Speed          |   11     Weight(lb)
          4      Idling         |   12     Customer ID
          5      Latitude       |   13     Customer Name
          6      Longitude      |   14     Customer Type
          7      Address        |   '''
        self.g1_lat = []
        self.g1_lon = []

        dt = datetime.datetime.now()

        mon = ("{:02d}".format(dt.month))
        day = ("{:02d}".format(dt.day))
        yr = ("{:02d}".format(dt.year)[2:])

        todays_date = (mon + "/" + day + "/" + yr)
        
        list_of_files = glob.glob('C:/Users/11048414/Downloads/*.xls')
        temp_latest_file = max(list_of_files, key=os.path.getctime)
        self.file_name = temp_latest_file[-10:-4]
        latest_file = temp_latest_file.replace('\\', '/')

        df = pd.read_html(latest_file)
        df = df[0]

        cur_g1 = df[df[0].str.contains(todays_date)]
                
        for lat in cur_g1[5]:
            self.g1_lat.append(lat)
        for lon in cur_g1[6]:
            self.g1_lon.append(lon)

    def send_to_db(self):
        self.table_name = ("G1B0024_" + self.file_name)
        drop_query=("DROP TABLE IF EXISTS {}").format(self.table_name)
        create_query = ("""CREATE TABLE IF NOT EXISTS {}  
                        (Latitude REAL,
                        Longitude REAL)""").format(self.table_name)
        insert_query =("insert into {} values (?, ?)").format(self.table_name) 

        try:
            sqliteConnection = sqlite3.connect('coordinates.db')
            cursor = sqliteConnection.cursor()
            
            cursor.execute(drop_query)
            cursor.execute(create_query)
            
            for i in range(len(self.g1_lat)):
                cursor.execute(insert_query, [self.g1_lat[i], self.g1_lon[i]])

            sqliteConnection.commit()
            cursor.close()
            
        except sqlite3.Error as error:
            print("Failed to insert data into database, " + str(error))
 
if __name__ == "__main__":
    test_app = g1b0024()
