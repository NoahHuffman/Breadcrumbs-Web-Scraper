import pandas as pd
import os
import glob
import datetime
import sqlite3

list_of_files = glob.glob('C:/Users/11048414/Downloads/*.xls')
temp_latest_file = max(list_of_files, key=os.path.getctime)
latest_file = temp_latest_file.replace('\\', '/')
file_name = temp_latest_file[-10:-4]

g1_lat = []
g1_lon = []

dt = datetime.datetime.now()

mon = ("{:02d}".format(dt.month))
day = ("{:02d}".format(dt.day))
yr = ("{:02d}".format(dt.year)[2:])

todays_date = (mon + "/" + day + "/" + yr)

df = pd.read_html(latest_file)
df = df[0]
print(file_name)

cur_g1 = df[df[0].str.contains(todays_date)]
      
for lat in cur_g1[5]:
    g1_lat.append(lat)
for lon in cur_g1[6]:
    g1_lon.append(lon)

    
table_name = ("G1B0024_"+file_name)
print(table_name)
drop_query=("DROP TABLE IF EXISTS {}").format(table_name)
create_query = ("""CREATE TABLE IF NOT EXISTS {}  
                   (Latitude REAL,
                   Longitude REAL)""").format(table_name)
insert_query =("insert into {} values (?, ?)").format(table_name) 

try:
    sqliteConnection = sqlite3.connect('coordinates.db')
    cursor = sqliteConnection.cursor()
    
    cursor.execute(drop_query)
    cursor.execute(create_query)
    

    for i in range(len(g1_lat)):
        cursor.execute(insert_query, [g1_lat[i], g1_lon[i]])

    sqliteConnection.commit()
    cursor.close()
    
except sqlite3.Error as error:
    print("Failed to insert data into database, " + str(error))




