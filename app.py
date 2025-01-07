# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy import create_engine
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
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
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

# Debug code
if __name__ == "__main__":
    app.run(debug=True)