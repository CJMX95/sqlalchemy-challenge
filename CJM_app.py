# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:////Users/Chase/bootcamp/hw/sqlalchemy-challenge/Resources/hawaii.sqlite')
# Relative path for some reason was not working, so I will use the absolute path to call the SQLite file

# Declare a Base using `automap_base()`
base = automap_base()

# Use the Base class to reflect the database tables
base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`# Assign the measurement class to a variable called `Measurement` and the station class to a variable called `Station`
measurement = base.classes.measurement
station = base.classes.station


# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Precipitation Analysis"""
    # Define the last available date
    last_date = dt.datetime.strptime('2017-08-17', '%Y-%m-%d')

    # Calculate the date 365 days before the last available date
    start_date = last_date - dt.timedelta(days=365)
    
    # Query Precipitation
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).all()
    session.close()

    # Convert the query results to a dictionary
    precip_data = {date: prcp for date, prcp in results}

    return jsonify(precip_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Stations"""
    # Query Stations
    results = session.query(station).all()
    session.close()

    # Convert the query results to a list of dictionaries
    station_data = []
    for result in results:
        station_data.append({
            "id": result.id,  # Replace with actual column names
            "name": result.name,  # Replace with actual column names
        })

    return jsonify(station_data)

# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Temprature Observations"""
 # Get the most active station
    most_active_station = session.query(measurement.station, func.count(measurement.station)) \
                                  .group_by(measurement.station) \
                                  .order_by(func.count(measurement.station).desc()) \
                                  .first()[0]

    # Calculate the date one year ago from the last available date
    last_date = dt.datetime.strptime('2017-08-17', '%Y-%m-%d')
    start_date = last_date - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the last year
    results = session.query(measurement.date, measurement.tobs) \
                     .filter(measurement.station == most_active_station) \
                     .filter(measurement.date >= start_date) \
                     .all()
    
    session.close()

    # Convert the query results to a list of dictionaries
    tobs_data = []
    for date, tobs in results:
        tobs_data.append({
            "date": date,
            "temperature": tobs
        })

    return jsonify(tobs_data)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start=None, end=None):
    
    # Convert dates to datetime format
    try:
        start = dt.strptime(start, "%Y-%m-%d")
        end = dt.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Min, Avg, Max Calculation"""
    
    # Query for TMIN, TAVG, TMAX for all dates greater than or equal to the start date
    default_end="2017-08-23"
    end = end if end else default_end

    results = session.query(
        func.min(measurement.tobs).label('TMIN'),
        func.avg(measurement.tobs).label('TAVG'),
        func.max(measurement.tobs).label('TMAX')
    ).filter(measurement.date >= start).all()

    session.close()

    # Check if results are empty
    if not results or results[0].TMIN is None:
        return jsonify({"error": "No data found for the specified start date."}), 404

    # NumPy Results
    np.ravel(results)
    results_list = list(results)
    return jsonify(results_list)

# Debug code
if __name__ == "__main__":
    app.run(debug=True)