"""
This script scrapes the dynamic data available through the Dublin Bikes API
It then adds it to the RDS database
It is being run every 5 mins on an EC2 instance using cron
Its print output is being added to a trace file on the EC2 instance
"""

from cmath import e
from datetime import datetime
import datetime
from tkinter import E
import requests
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
from pprint import pprint
import time
from IPython.display import display
import pymysql
import json
db = pymysql.connect(
    host="dbbikes.ccmhqwttjfav.us-east-1.rds.amazonaws.com",
    user="admin",
    password="12345678",
    port=3306,
    database="dbbikes")
cursor=db.cursor()



sql="""
CREATE  TABLE IF NOT EXISTS station(
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
status VARCHAR(256)
)
"""
try:
    cursor.execute(sql)
except Exception as e:
    print(e)
sql="""
CREATE TABLE IF NOT EXISTS availability(
number INTEGER,
available_bikes INTEGER,
available_bike_stands INTEGER,
last_update INTEGER
)

"""
try:
    cursor.execute(sql)
except Exception as e:
    print(e)

api_key = "fc31aed31ee8e2ae5c2a3f75172b9167873f1bc9"
URL = "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=" + api_key

def write_to_file(text):
    with open("data/bike_{}".format(now).replace(" ","_"),"w") as f:
        f.write(r.text)

def write_to_db(text):
    print(text)

def main():
    while True: 
        try:
        # Make the get request
            now=datetime.datetime.now()
            r = requests.get(url=URL)
            print(r,now)
            write_to_file(r.text)
            write_to_db(r.text)
            time.sleep(5*60)
        except requests.exceptions.RequestException as err:
            print("SOMETHING WENT WRONG:", err)
            exit(1)
    return
def stations_to_db(text):
    stations=json.loads(text)
    print(type(stations),len(stations))
    for station in stations:
        print("&&&&&&&&&")
        print(station)
        print("*******")
        vals=(station.get('address'),int(station.get('banking')),station.get('bike_stands'),int(station.get('bonus')),station.get('contract_name'),station.get('name'),station.get('number'),station.get('position').get('lat'),
        station.get('position').get('lng'),station.get('status')
        )
        vals1=(station.get('number'),station.get('available_bikes'),station.get('available_bike_stands'),station.get('last_update')
        )
        print(vals1)
        cursor.execute("INSERT INTO station values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",vals)
        db.commit()
        cursor.execute("INSERT INTO availability values(%s,%s,%s,%s)",vals1)
        db.commit()

        

stations_to_db(r.text)

db.close()





    