"""
This script scrapes the dynamic data available through the Dublin Bikes API
It then adds it to the RDS database
It is being run every 5 mins on an EC2 instance using cron
Its print output is being added to a trace file on the EC2 instance
"""
import datetime as dt
import requests
import time
import pymysql
import json
import pytz
NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"
APIKEY = "e2e86989774502711e895376db54cddc35bd6d30"
USER = "admin"
PASSWORD = "12345678"
HOST = "dbbikes1.citjnbrbkplf.us-east-1.rds.amazonaws.com"
PORT = 3306
DATABASE = "dbbikes1"
r = requests.get("https://api.jcdecaux.com/vls/v1/stations?apiKey=e2e86989774502711e895376db54cddc35bd6d30&contract=Dublin")

def initialise_db():
    sql="""
      CREATE TABLE IF NOT EXISTS station(
        number INTEGER PRIMARY KEY,
        name VARCHAR(128),
        address VARCHAR(128),
        position_lat DOUBLE,
        position_lng DOUBLE,
        bike_stands INTEGER,
        banking INTEGER,
        bonus INTEGER,
        contract_name VARCHAR(128)
    )
    """
    try:
        cursor.execute(sql)
    except Exception as e:
        print(e)
    sql="""
    CREATE TABLE IF NOT EXISTS availability(
        number INTEGER ,
        last_update DateTime ,
        available_bike_stands INTEGER,
        available_bikes INTEGER,
        status VARCHAR(128),
        primary key (number,last_update ) 

    )

    """
    try:
        print(sql)
        cursor.execute(sql)
        print("create ok")
    except Exception as e:
        print(e)
    write_to_db_sation()
    


def get_stations():
    stationList=[]
    stations=json.loads(r.text)
    for station in stations:
        vals_station=(
            int(station.get('number')),
            station.get('name'),
            station.get('address'),
            float(station.get('position').get('lat')),
            float(station.get('position').get('lng')),
            int(station.get('bike_stands')),
            int(station.get('banking')),
            int(station.get('bonus')),
            station.get('contract_name')
            )
        stationList.append(vals_station)
    return stationList

#GetNoStaticData
def get_availability():
    availList=[]
    stations=json.loads(r.text)
    for station in stations:
        vals_availability=(
        station.get('number'),
        dt.datetime.fromtimestamp(int(station.get('last_update') / 1e3)),
        station.get('available_bike_stands'),
        station.get('available_bikes'),
        station.get('status')      
            )
        availList.append(vals_availability)
    return availList

def write_to_db_sation():
    vals= get_stations()
    try:
        for val in vals:
            sql = """INSERT INTO dbbikes1.station (number,name,address,position_lat,position_lng,bike_stands,banking,bonus,contract_name) 
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % vals
            cursor.execute(sql)
            db.commit()
            print("insert ok")
    except:
        db.rollback()
        print("insert wrong")

def write_to_db__availability():
    vals= get_availability()
    try:
        for val in vals:
            sql = """INSERT INTO dbbikes1.availability(number,last_update,available_bike_stands,available_bikes,status) 
            VALUES (%s,'%s',%s,%s,'%s')""" % val
            print(sql)
            a=cursor.execute(sql)
            db.commit()
            print(a)
            print("insert ok")
    except:
        db.rollback()
        print("insert wrong")
    db.close()
    

db = pymysql.connect(
host=HOST,
user=USER,
password=PASSWORD,
port=PORT,
database=DATABASE)
cursor = db.cursor()  
initialise_db() 
db.close()
while True:
    r = requests.get("https://api.jcdecaux.com/vls/v1/stations?apiKey=e2e86989774502711e895376db54cddc35bd6d30&contract=Dublin")
    db = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        database=DATABASE)
    cursor = db.cursor()  
    
    
        # Get the current time in Dublin
    #now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin')).time()
        #Not necessary to get data in the evening, so judge the time
    #if now >= dt.time(5, 0) or now <= dt.time(0, 30): 
        
    write_to_db__availability()
    time.sleep(5*60)
    






    