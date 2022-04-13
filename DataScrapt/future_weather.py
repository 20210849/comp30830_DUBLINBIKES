import pymysql 
import traceback
import requests
import time
from datetime import datetime
import json

weather_apiKey = "c52ab5b9c342a6c8e1bf83b83bd3313a"
lat = 53.3498
lon = 6.2603
part = "current,daily,minutely"
parameters = {"lat": lat, "lon": lon, "exclude": part, "appid" : weather_apiKey} 
weather_URL = "https://api.openweathermap.org/data/2.5/onecall"

def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS future_weather(
    clouds INTEGER,
    dew_point DOUBLE,
    dt VARCHAR(255),
    feels_like DOUBLE,
    humidity INTEGER,
    pop DOUBLE,
    pressure INTEGER,
    temp DOUBLE,
    uvi DOUBLE,
    visibility INTEGER,
    weather_description VARCHAR(255),
    weather_main VARCHAR(255),
    wind_deg INTEGER,
    wind_gust DOUBLE,
    wind_speed DOUBLE
    );
    """   
    try:
        res = cursor.execute(sql)
        print('create ok')
    except Exception as e:
        print(e)

def write_to_db(text):
    future_weather_data = json.loads(text)
    for future_hour in range(len(future_weather_data['hourly'])):
        weather_vals = (
            str(future_weather_data['hourly'][future_hour]['clouds']), 
            str(future_weather_data['hourly'][future_hour]['dew_point']),
            str(datetime.fromtimestamp(future_weather_data['hourly'][future_hour]['dt'])),
            str(future_weather_data['hourly'][future_hour]['feels_like']),
            str(future_weather_data['hourly'][future_hour]['humidity']), 
            str(future_weather_data['hourly'][future_hour]['pop']),
            str(future_weather_data['hourly'][future_hour]['pressure']), 
            str(future_weather_data['hourly'][future_hour]['temp']),
            str(future_weather_data['hourly'][future_hour]['uvi']),
            str(future_weather_data['hourly'][future_hour]['visibility']),
            str(future_weather_data['hourly'][future_hour]['weather'][0]['description']), 
            str(future_weather_data['hourly'][future_hour]['weather'][0]['main']),
            str(future_weather_data['hourly'][future_hour]['wind_deg']), 
            str(future_weather_data['hourly'][future_hour]['wind_gust']),
            str(future_weather_data['hourly'][future_hour]['wind_speed'])
            )
        
        sql = """INSERT INTO dbbikes1.future_weather (clouds,dew_point,dt,feels_like,humidity,
        pop,pressure,temp,uvi,visibility,weather_description,weather_main,wind_deg,wind_gust,wind_speed) 
        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % weather_vals
    
        try:
            cursor.execute(sql)
            db.commit()
            print("insert ok")
        except:
            db.rollback()
            print("insert wrong")
    db.close()

while True:
    try:
        db = pymysql.connect(
            host="dbbikes1.citjnbrbkplf.us-east-1.rds.amazonaws.com",
            user="admin",
            password="12345678",
            port=3306,
            database="dbbikes1")
        cursor = db.cursor()  

        create_table()

        now = datetime.now()
        r = requests.get(weather_URL, params = parameters)
        print(r,now)
            
        write_to_db(r.text)
            
        time.sleep(48*60*60)
        
    except:
        print(traceback.format_exc())   