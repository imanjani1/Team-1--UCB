# Import dependencies
from flask import Flask, render_template, jsonify

import os
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import func, or_, and_
from sqlalchemy import desc

#############################################################################
# USING PANDAS TO COLLECT DATA
#############################################################################
# _csvpath = os.path.join('DataSets', 'belly_button_biodiversity_samples.csv')
# #_csvpath = os.path.join('belly_button_biodiversity_samples.csv')
# _data = pd.read_csv(_csvpath)
# column_names = list(_data.columns)
# del column_names[0]
#############################################################################
# USING SQLALCHEMY TO FIND THE sample names -- **IMPORTANT NOTE** - if running
# queries OUTSIDE of app function, it will create a different thread, thereby
# running another query INSIDE the app function will require another connection
# to the DB.  **IMPORTANT NOTE**
##############################################################################

if not os.path.exists('uber_lyft_DB.sqlite'):
    raise FileNotFoundError("The UL-sqlite-file does not exist")
engine = create_engine("sqlite:///uber_lyft_DB.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

ridesharedata = Base.classes.rideshare

session = Session(engine)

##############################################################################

app = Flask(__name__)

#################################################
# Routes
#################################################

# Main route 
@app.route('/')
def home():
    return render_template('index.html', text = "Number of Pickups/Dropoffs according to time of day")

@app.route('/daysnumber')
def info():

    ridesharecolumns = ridesharedata.__table__.columns.keys()
    return jsonify(ridesharecolumns)

@app.route('/pickups/<day>')
def pickup_info(day):

    dow_query = (session.query(ridesharedata.hour, func.sum(ridesharedata.pickups)).
                group_by(ridesharedata.hour).filter(ridesharedata.day_of_week == day).all())

    dow_list = []

    for each in dow_query:
        dow_dict = {}
        dow_dict['hour'] = each[0]
        dow_dict['total_pickups'] = each[1]
        dow_list.append(dow_dict)

    return jsonify(dow_list)

@app.route('/dropoffs/<day>')
def dropoff_info(day):

    dow_query = (session.query(ridesharedata.hour, func.sum(ridesharedata.dropoffs)).
                group_by(ridesharedata.hour).filter(ridesharedata.day_of_week == day).all())

    dow_list = []

    for each in dow_query:
        dow_dict = {}
        dow_dict['hour'] = each[0]
        dow_dict['total_dropoffs'] = each[1]
        dow_list.append(dow_dict)

    return jsonify(dow_list)

@app.route('/hours/<hour>')
def hour_info(hour):

    hour_query = (session.query(ridesharedata.trip_area, ridesharedata.latitude, ridesharedata.longitude, ridesharedata.name, 
                    ridesharedata.day_of_week, ridesharedata.hour, ridesharedata.pickups, ridesharedata.dropoffs).filter(
                            ridesharedata.hour == hour).all())

    hour_list = []

    for each in hour_query:
        hour_dict = {}
        hour_dict['trip_area'] = each[0]
        hour_dict['latitude'] = each[1]
        hour_dict['longitude'] = each[2]
        hour_dict['day_of_week'] = each[3]
        hour_dict['hour'] = each[4]
        hour_dict['pickups'] = each[5]
        hour_dict['dropoffs'] = each[6]
        hour_list.append(hour_dict)

    return jsonify(hour_list)



if __name__ == "__main__":
    app.run(debug=True)
