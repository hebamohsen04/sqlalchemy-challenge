import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt 

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2012-02-28<br/>"
        f"/api/v1.0/2012-02-28/2012-03-05<br/>"
    )


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    last_date_record = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.date.fromisoformat(last_date_record[0])

    # Calculate the date 1 year ago from the last data point in the database
    last_year = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    session.close()
    
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
        
    return jsonify(all_prcp)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    results= session.query(Station.station).all()
    session.close()
    
    all_names = list(np.ravel(results))
    
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    most_active_station = most_active_stations[0]
    
    last_date_record = session.query(Measurement.date).\
    filter(Measurement.station == most_active_station[0]).\
    order_by(Measurement.date.desc()).first()
    
    last_date = dt.date.fromisoformat(last_date_record[0])
    
    # Calculate the date 1 year ago from the last data point in the database
    last_year = last_date - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).all()
    session.close()
    
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def temps_with_start(start):
    result = calc_temps_start(start)
    #TMIN, TAVG, and TMAX
    dict = {
        "TMIN" : result[0][0],
        "TAVG" : result[0][1],
        "TMAX" : result[0][2],
        "start" : start
    }
    return jsonify(dict)

@app.route("/api/v1.0/<start>/<end>")
def temps_with_start_end(start, end):
    result = calc_temps_start_end(start, end)
    #TMIN, TAVG, and TMAX
    dict = {
        "TMIN" : result[0][0],
        "TAVG" : result[0][1],
        "TMAX" : result[0][2],
        "start" : start,
        "end" : end
    }
    return jsonify(dict)

def calc_temps_start(start_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()
    session.close()
    return results

def calc_temps_start_end(start_date, end_date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    return results


if __name__ == "__main__":
    app.run(debug=True)
