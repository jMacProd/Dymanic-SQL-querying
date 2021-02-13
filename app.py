import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#Define dictionary
hello_dict = {"Hello": "World"}

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"<h2>Welcome to the Honolulu Climate Analysis API</h2>"
        f"<h3>Available routes are:</h3>"
        f"<h4>Static Routes</h4>"

        f"<p>Precipitation data for dates 2016-08-23 to 2017-08-23</br>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></p>"

        f"<p>Observation stations inlcuding location details and observation count</br>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a></p>"

        f"<p>Temperature data for the most active station (WAIKIKI 717.2, HI US) </br>"
        f"for dates 2016-08-23 to 2017-08-23.</br>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></p>"

        f"<h4>Dynamic Routes</h4>"

        f"<p>Route accepts the date parameters (yyyy-mm-dd) in the url to return the <br>"
        f"minimum, average and maximum temperature for a given start or start-end range.</br>"
        f"<em>Full data range is 2010-01-01 to 2017-08-23</em><br/><br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end</p>"

    )

#################################################
# Precipitation
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query to retrieve the last 12 months of precipitation data and plot the results
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').all()

    #precip = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Convert list of tuples into normal list
    #preciplist = list(np.ravel(precip))

    # Create a dictionary from the row data and append to a list of all_passengers
    precipitation = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict[date] = prcp
        #precip_dict["prcp"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)

#################################################
# Stations
#################################################
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")

    session = Session(engine)

    #Return a JSON list of stations from the dataset - list includes observation count
    stationtempobsmost = session.query(Measurement.station, Station.name, Station.latitude, Station.longitude, Station.elevation, func.count(Measurement.station))\
        .filter(Measurement.station == Station.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).all()

    session.close()

    stationlist = []
    for station, name, lat, long, elev, count in stationtempobsmost:
        station_dict = {}
        station_dict["station_id"] = station
        station_dict["name"] = name
        station_dict["lat"] = lat
        station_dict["long"] = long
        station_dict["elev"] = elev
        station_dict["count"] = count
        stationlist.append(station_dict)

    return jsonify(stationlist)

#################################################
# tobs 
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data.
    #base columms
    stationtempobs = [Measurement.station, Station.name, Measurement.date, Measurement.tobs]

    #Query the station with the highest oberservation count
    stationtempobsmost = session.query(*stationtempobs, func.count(Measurement.station))\
        .filter(Measurement.station == Station.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()
        
    stationtotalobs = stationtempobsmost[0]
    
    waiheetempobs = session.query(*stationtempobs)\
        .filter(Measurement.station == Station.station)\
        .filter(Measurement.date >= '2016-08-23')\
        .filter(Measurement.date <= '2017-08-23')\
        .filter(Measurement.station==stationtotalobs)

    session.close()

    waiheelist = []
    for station, name, date, temp in waiheetempobs:
        waihee_dict = {}
        waihee_dict["station_id"] = station
        waihee_dict["name"] = name
        waihee_dict["date"] = date
        waihee_dict["temp"] = temp
        waiheelist.append(waihee_dict)

    return jsonify(waiheelist)

#################################################
# Start Date 
#################################################
#@app.route("/api/v1.0/justice-league/real_name/<real_name>")
    # I think how the justice one works is real_name is the index, <real_name> is the value that you input
    # So for start date, judging by the provided the the actual date is the index>?
@app.route("/api/v1.0/<start>")

#def justice_league_by_real_name(real_name):
def start_date(start):
    print("Server received request for 'Start Date' page...")

    session = Session(engine)

    #convert to datetime
    #startdt = dt.datetime.strptime(start, '%Y/%m/%d')
    #enddt = dt.datetime.strptime('2017-08-23', '%Y/%m/%d')

    #Calculate start and end dates for the prevoius year
    #start_date = startdt - dt.timedelta(days=365)
    #start_date = start
    
    Startsummary = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= '2017-08-23').all()

    session.close()

    startlist = [
    #for min, av, max  in Startsummary:
    #start_dict =
    {
    "minimum": Startsummary[0][0],
    "average": Startsummary[0][1],
    "maximum": Startsummary[0][2]}]
    #waiheelist.append(waihee_dict)

    return jsonify(startlist)

#################################################
# Start End Date 
#################################################
@app.route("/api/v1.0/<start>/<end>")
def end_date(start, end):

    session = Session(engine)

    #start_date = start
    #end_date = end

    Startendsummary = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    startendlist = [
    #for min, av, max  in Startsummary:
    #start_dict =
    {
    "minimum": Startendsummary[0][0],
    "average": Startendsummary[0][1],
    "maximum": Startendsummary[0][2]}]
    #waiheelist.append(waihee_dict)

    return jsonify(startendlist)

#def justice_league_character(real_name):
#    """Fetch the Justice League character whose real_name matches
#       the path variable supplied by the user, or a 404 if not."""

#    canonicalized = real_name.replace(" ", "").lower()
#    for character in justice_league_members:
#        search_term = character["real_name"].replace(" ", "").lower()

#        if search_term == canonicalized:
#            return jsonify(character)

#    return jsonify({"error": f"Character with real_name {real_name} not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)

