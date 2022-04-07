from ctypes.wintypes import PLARGE_INTEGER
import json
import pymysql
from sqlalchemy import *
from sqlalchemy import Table, Column, Integer, Float, String, DateTime
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from flask import Flask, render_template, request
from jinja2 import Template
from sqlalchemy import create_engine, select, MetaData, Table, and_
import pandas as pd
from joblib import dump, load

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

    sql = "SELECT s.number, s.name, s.address, s.position_lat, s.position_lng, a.available_bike_stands, a.available_bikes, " \
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
def predict(station_id):
    model = load('availabilitypredictions.joblib')
    avail_predict = model.predict([[station_id, 2, 5, 2, 4]])

    predict_list = avail_predict.tolist()
    predict_dict = {"bikes": predict_list[0]}
    result = json.dumps(predict_dict)

    return result



if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8080, debug=False)
