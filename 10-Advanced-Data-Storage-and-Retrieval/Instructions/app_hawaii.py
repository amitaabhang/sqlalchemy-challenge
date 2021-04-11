# 1. import Flask
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=True, connect_args={"check_same_thread": False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Base.classes.keys()

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

results =session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

recent_date = dt.datetime.strptime(results , '%Y-%m-%d')

new_date = recent_date - dt.timedelta(days = 365)

results_stn = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
.order_by(func.count(Measurement.station).desc()).all()
active_station_id = results_stn[0][0]

prcp_results = session.query(Measurement.date, Measurement.prcp).all()

station_results = session.query(Station.station).all()

recentyear_temp_results =session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= new_date).filter(Measurement.station == active_station_id).all()
    

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. List all routes that are available.
@app.route("/")
def home():
    return (
        f"Welcome to the Mesaurements and Station API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br><br/>"
    )

#4. Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prec = {result[0]:result[1] for result in prcp_results}
    return jsonify(prec)

#5. Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    np_result = list(np.ravel(station_results))
    return jsonify(stations = np_result)

#6. Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    np_temp_result = list(np.ravel(recentyear_temp_results))
    return jsonify(Date_Temp = np_temp_result)

#7 Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end = None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date > start).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)
    else:
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        final_result = list(np.ravel(results))
        return jsonify(temps = final_result)


if __name__ == "__main__":
    app.run(debug=True)
