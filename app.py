# Import Dependenices 
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
#Create engine
engine = create_engine("sqlite:///hawaii.sqlite",connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
#inspect
inspector = inspect(engine)
columns = inspector.get_columns('measurement')
for header in columns:
    print(header['name'], header['type'])
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#Define what to do when a user hits the index route
#home page and all other routes
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/ + start date<br>"
        f"/api/v1.0/ + start date/ + end date"
    )
#Define what to do when a user hits precip route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = latest_date[0]
    one_year = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precip_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    precip_data = list(np.ravel(precip_query))
    return jsonify(precip_data)
    
#Define what to do when a user hits station route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    station_query = session.query(station.station).all()
    station_data = list(np.ravel(station_query))
    return jsonify(station_data)

#Define what to do when a user hits temp route
@app.route("/api/v1.0/tobs")
def temperature():
    print("Server received request for 'Temperature' page...")
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    latest_date = latest_date[0]
    one_year = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)
    tobs_query = session.query(measurement.date, measurement.tobs).filter(measurement.date >= one_year).all()
    tobs_data = list(np.ravel(tobs_query))
    return jsonify(tobs_data)

#Define list of calculated temp when enter start and end date
@app.route("/api/v1.0/<start>")
def start_date(start=None):
    print("Server received request for 'Start Date' page...")
    start_query = session.query(measurement.tobs).filter(measurement.date >= start).all()
    df = pd.DataFrame(start_query)
    tmin = df.min()
    tavg = df.mean()
    tmax = df.max()
    temp_data = [tmin, tavg, tmax]
    temp_data = list(np.ravel(temp_data ))
    return jsonify(temp_data )

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    print("Server received request for 'End Date' page...")
    end_query = session.query(measurement.tobs).filter(measurement.date >= start).filter(measurement.date <= end).all()
    df = pd.DataFrame(end_query) 
    tmin = df.min()
    tavg = df.mean()
    tmax = df.max()
    temp_data = [tmin, tavg, tmax]
    temp_data = list(np.ravel(temp_data))
    return jsonify(temp_data)
    
#final
if __name__ == '__main__':
    app.run(debug=True)