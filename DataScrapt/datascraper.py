from http.client import ImproperConnectionState
from shutil import register_unpack_format
import datetime as dt
import traceback
from tracemalloc import start
from pymysql import IntegrityError
import requests
import pytz
import time
from sqlalchemy import *
from sqlalchemy import Table, Column, Integer, Float, String, DateTime
from sqlalchemy import MetaData
from sqlalchemy import create_engine

NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"
APIKEY = "e2e86989774502711e895376db54cddc35bd6d30"
USER = "admin"
PASSWORD = "12345678"
HOST = "dbbikes1.citjnbrbkplf.us-east-1.rds.amazonaws.com"
PORT = "3306"
DATABASE = "dbbikes1"
engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, HOST, PORT, DATABASE), echo=True)
connection = engine.connect()
r = requests.get("https://api.jcdecaux.com/vls/v1/stations?apiKey=e2e86989774502711e895376db54cddc35bd6d30&contract=Dublin")

def initialise_db():
    # Generate a metaDate object
    metadata = MetaData(bind=engine)

    with engine.connect() as conn:
        # Create a static data table and determine if there is a station table
        if engine.dialect.has_table(conn, "station") is False:
            station = Table('station', metadata,
                            Column('number', Integer, primary_key=True),
                            Column('name', String(128)),
                            Column('address', String(128)),
                            Column('position_lat', Float),
                            Column('position_lng', Float),
                            Column('bike_stands', Integer),
                            Column('banking', Integer),
                            Column('bonus', Integer),
                            Column('contract_name', String(128))
                            )

            try:
                metadata.create_all(engine)
                # Get station data
                values = map(get_stations, r.json())
                # Write static data first
                write_to_db("station", values)
            except:
                traceback.format_exc()
        #Create dynamic data tables availability
        if engine.dialect.has_table(conn, "availability") is False:
            availability = Table('availability', metadata,
                                 Column('number', Integer, primary_key=True),
                                 Column('last_update', DateTime, primary_key=True),
                                 Column('available_bike_stands', Integer),
                                 Column('available_bikes', Integer),
                                 Column('status', String(128)))

            try:
                #Because dynamic data needs to be captured in real time, create only tables first
                metadata.create_all(engine)
            except:
                traceback.formal_exc()

        return

# Write static data to station table
def write_to_db(table_name, values):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables.get(table_name)

    with engine.connect() as connection:
        for val in values:
            try:
                res = connection.execute(table.insert().values(val))
            except IntegrityError as err:
                return
#GetStaticData
def get_stations(s):
    return {'number': s['number'], 'name': s['name'], 'address': s['address'], 'position_lat': s['position']['lat'], 'position_lng': s['position']['lng'], 'bike_stands': s['bike_stands'], 'banking': s['banking'], 'bonus': s['bonus'], 'contract_name': s['contract_name']}
#Access to dynamic data
def get_availability(s):
    if 'last_update' not in s or s['last_update'] is None:
        return None
    return {'number': int(s['number']), 'available_bike_stands': int(s['available_bike_stands']),
            'available_bikes': int(s['available_bikes']),
            'last_update': dt.datetime.fromtimestamp(int(s['last_update'] / 1e3)), 'status': s['status']}
# Write dynamic data
def store_availability():
    try:
        values = filter(lambda x: x is not None, map(get_availability, r.json()))
        write_to_db('availability', values)
    except:
        traceback.format_exc()

    return
#main function
def main():
    # First initialize the database
    initialise_db()
    #Cyclic capture of dynamic data.
    while True:
        # Get the current time in Dublin
        now = dt.datetime.now(tz=pytz.timezone('Europe/Dublin')).time()
        #Not necessary to get data in the evening, so judge the time
        if now >= dt.time(5, 0) or now <= dt.time(0, 30): 
            store_availability()

        time.sleep(5 * 60)

    return


if __name__ == "__main__":
    main()
