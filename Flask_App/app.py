from ctypes.wintypes import PLARGE_INTEGER
import json
import pickle
import pymysql
from sqlalchemy import *
from sqlalchemy import Table, Column, Integer, Float, String, DateTime
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from flask import Flask, jsonify, render_template, request
from jinja2 import Template
from sqlalchemy import create_engine, select, MetaData, Table, and_
import pandas as pd
from joblib import dump, load
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"
APIKEY = "e2e86989774502711e895376db54cddc35bd6d30"
USER = "admin"
PASSWORD = "12345678"
HOST = "dbbikes1.citjnbrbkplf.us-east-1.rds.amazonaws.com"
PORT = "3306"
DATABASE = "dbbikes1"

@app.route("/")
def hello():
    #return 'Welcome to My Watchlist!'

    return render_template("index.html")


@app.route("/stations")
def stations():
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    connection = engine.connect()   

    sql = "SELECT s.number,s.bike_stands, s.name, s.address, s.position_lat, s.position_lng, a.available_bike_stands, a.available_bikes, " \
          "a.status, MAX(a.last_update) AS `current_availability` " \
          "FROM dbbikes1.availability as a " \
          "INNER JOIN dbbikes1.station as s ON s.number = a.number " \
          "GROUP BY s.number " \
          "ORDER BY s.number;"

    df = pd.read_sql(sql, engine)
    print(df)

    return df.to_json(orient="records")


@app.route("/static_stations")
def static_stations():
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    connection = engine.connect()  

    sql = "SELECT * FROM dbbikes1.station " \
          "ORDER BY name;"

    df = pd.read_sql(sql, engine)

    return df.to_json(orient="records")


@app.route('/occupancy/<int:station_id>')
def get_occupancy(station_id):
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    connection = engine.connect()  

    sql = f"""SELECT s.name, avg(a.available_bike_stands) as Avg_bike_stands,
        avg(a.available_bikes) as Avg_bikes_free, DAYNAME(a.last_update) as DayName
        FROM dbbikes1.availability as a
        JOIN dbbikes1.station as s
        ON s.number = a.number
        WHERE s.number = {station_id}
        GROUP BY s.name , DayName 
        ORDER BY s.name , DayName;"""

    df = pd.read_sql(sql, engine)

    return df.to_json(orient="records")


@app.route('/hourly/<int:station_id>')
def get_hourly_data(station_id):
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    connection = engine.connect()  

    sql = f"""SELECT s.name,count(a.number),avg(available_bike_stands) as Avg_bike_stands,
        avg(available_bikes) as Avg_bikes_free,EXTRACT(HOUR FROM last_update) as Hourly
        FROM dbbikes1.availability as a
        JOIN dbbikes1.station as s
        ON s.number = a.number
        WHERE a.number = {station_id}
        GROUP BY EXTRACT(HOUR FROM last_update) 
        ORDER BY EXTRACT(HOUR FROM last_update) asc"""

    df = pd.read_sql(sql, engine)

    return df.to_json(orient="records")

@app.route("/weather_forecast")
def weather_forecast():
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    connection = engine.connect()  
    print("************************")

    sql = f"""SELECT weather_description, weather_main, humidity, wind_speed
    FROM dbbikes1.weather_Dublin
    ORDER BY dt DESC
    LIMIT 1;"""

    df = pd.read_sql(sql, engine)

    return df.to_json(orient="records")

@app.route('/predict/<int:station_id>')
def predict_station(station_id):
    print("************************")

    with open('./static/pklFile/model_{}.pkl'.format(station_id), 'rb') as handle:
        model = pickle.load(handle)
        prediction = model.predict([[9.0,56.0,283.67,79.0,1009.0,75.0,10000.0,9.26,0,0,0,0,0,1,0,0,1,0,0]])
        print("pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine pklfine")
        
        predict_list = prediction.tolist()
        result = str(predict_list[0])

        print(result)
        return result

    # input_model = station_dfs[ID][modelfeatures]
    # output = station_dfs[ID]['available_bikes']
    # modelfeature = ['hour_x','minute_x', 'temp', 'humidity', 'pressure', 'Clouds', 'visibility',
    # 'wind_speed', 'weekday_Friday', 'weekday_Monday', 'weekday_Saturday','weekday_Sunday', 'weekday_Thursday', 'weekday_Tuesday',
    # 'weekday_Wednesday', 'weather_main_Clear', 'weather_main_Clouds', 'weather_main_Drizzle', 'weather_main_Rain']
    
    # station_dfs = dict()
    # station_dfs[station_number] = [9.0,56.0,283.67,79.0,1009.0,75.0,10000.0,9.26,0,0,0,0,0,1,0,0,1,0,0]
    # X_test = station_dfs[station_number][0]


    # engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
    # connection = engine.connect()  

    # sql = "SELECT temp, humidity, pressure, Clouds, visibility, wind_speed, dt, weather_main FROM dbbikes1.weather_Dublin " \
    #    "ORDER BY dt DESC " \
    #    "LIMIT 1;" 
        
    # weather = pd.read_sql(sql, engine)
    ### used in ML learning 
    ### if else sentence to change 'dt' into 'weekday_Monday' and so on ...
    ### if else sentence to change 'weather_main' into 'weather_main_Clear' and so on ...
    

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8080, debug=False)
