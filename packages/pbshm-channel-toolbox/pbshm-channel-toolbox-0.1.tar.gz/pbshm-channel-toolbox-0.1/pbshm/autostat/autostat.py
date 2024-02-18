import math
import statistics
from datetime import datetime
from random import randint

from bokeh import colors
from bokeh.embed import components
from bokeh.plotting import figure
from flask import Blueprint, render_template, request, jsonify

from pbshm.authentication import authenticate_request
from pbshm.db import default_collection
from pbshm.timekeeper import datetime_to_nanoseconds_since_epoch, convert_nanoseconds

#Create the Autostat Blueprint
bp = Blueprint(
    "autostat",
    __name__,
    template_folder="templates"
)

#Calculate Statistics Data
def calculate_statistical_analysis(channel_y, channel_value_sum, channel_mean, channel_median, channel_std, channel_skew, channel_kurtosis, normalise=True):
    #Enumerate through the channels
    for name in channel_y:
        #Ensure Values
        if len(channel_y[name]) == 0: continue
        #Calculate Basic Statistics
        n = float(len(channel_y[name]))
        mean = channel_value_sum[name]/n
        channel_median[name] = statistics.median(channel_y[name])
        #Calculate moments
        second_moment_sum, third_moment_sum, fourth_moment_sum = 0.0, 0.0, 0.0
        for value in channel_y[name]:
            moment = value-mean
            second_moment = moment*moment
            third_moment = second_moment*moment
            second_moment_sum += second_moment
            third_moment_sum += third_moment
            fourth_moment_sum += third_moment*moment
        #Calculate Moment based statistics
        std = math.sqrt(second_moment_sum/n)
        channel_skew[name] = math.sqrt(n)*(third_moment_sum/(second_moment_sum**1.5)) if second_moment_sum != 0 else 0
        channel_kurtosis[name] = n*(fourth_moment_sum/(second_moment_sum**2)) if second_moment_sum != 0 else 0
        channel_mean[name] = mean
        channel_std[name] = std
        #Normalise values
        if normalise and std != 0: channel_y[name] = [(value-mean)/std for value in channel_y[name]]

#Details JSON View
@bp.route("/populations/<population>")
@authenticate_request("autostat-statistics")
def population_details(population):
    populations=[]
    for document in default_collection().aggregate([
        {"$match":{"population":population}},
        {"$project":{
            "_id":0,
            "population":1,
            "timestamp":1,
            "channels.name":1,
            "channels.type":1,
            "channels.unit":1
        }},
        {"$group":{
            "_id":"$population",
            "start":{"$first":"$timestamp"},
            "end":{"$last":"$timestamp"},
            "channels":{"$addToSet":"$channels"}
        }},
        {"$project":{
            "_id":0,
            "name":"$_id",
            "start":1,
            "end":1,
            "channels":{
                "$reduce":{
                    "input":{
                        "$reduce":{
                            "input":"$channels",
                            "initialValue":[],
                            "in":{"$concatArrays":["$$value", "$$this"]}
                        }
                    },
                    "initialValue":[],
                    "in":{"$concatArrays":["$$value",{"$cond":[{"$in":["$$this","$$value"]},[],["$$this"]]}]}
                }
            }
        }},
        {"$unwind":"$channels"},
        {"$group":{
            "_id":{
                "type":"$channels.type",
                "unit":"$channels.unit"
            },
            "name":{"$first":"$name"},
            "start":{"$first":"$start"},
            "end":{"$last":"$end"},
            "channels":{"$addToSet":"$channels.name"}
        }},
        {"$group":{
            "_id":None,
            "name":{"$first":"$name"},
            "start":{"$first":"$start"},
            "end":{"$last":"$end"},
            "types":{"$addToSet":{
                "name":"$_id.type",
                "unit":"$_id.unit",
                "channels":"$channels"
            }}
        }},
        {"$project":{"_id":0}},
        {"$limit":1}
    ]):
        populations.append(document)
    return jsonify(populations[0]) if len(populations) > 0 else jsonify()

#List View
@bp.route("/populations")
@authenticate_request("autostat-list")
def population_list(link_name = "view", link_endpoint = "autostat.population_statistics"):
    populations=[]
    for document in default_collection().aggregate([
        {"$group":{
            "_id": "$population",
            "structure_names": {"$addToSet": "$name"},
            "channel_names": {"$addToSet": "$channels.name"},
            "start_date": {"$first": "$timestamp"},
            "end_date": {"$last": "$timestamp"}
        }},
        {"$project":{
            "_id": 0,
            "population_name": "$_id",
            "structure_names": 1,
            "channel_names": 1,
            "start_date": 1,
            "end_date": 1
        }},
        {"$sort": {"population_name": 1}}
    ]):
        document["link_name"] = link_name
        document["link_endpoint"] = link_endpoint
        document["start_date_time"] = convert_nanoseconds(document["start_date"], "datetime")
        document["end_date_time"] = convert_nanoseconds(document["end_date"], "datetime")
        populations.append(document)
    return render_template("list-populations.html", populations=populations)

#Statistics View
@bp.route("/populations/<population>/statistics", methods=("GET", "POST"))
@authenticate_request("autostat-statistics")
def population_statistics(population):
    #Load All Populations
    populations=[]
    for document in default_collection().aggregate([
        {"$group":{"_id":"$population"}},
        {"$sort":{"_id":1}}
    ]):
        populations.append(document["_id"])
    #Handle Request
    error, js, html, channels=None, None, None, []
    channel_colour, channel_mean, channel_median, channel_std, channel_skew, channel_kurtosis = {}, {}, {}, {}, {}, {}
    if request.method == "POST":
        #Validate Inputs
        startDate = request.form["start-date"]
        startTime = request.form["start-time"]
        endDate = request.form["end-date"]
        endTime = request.form["end-time"]
        channels = request.form.getlist("channels")
        startDateParts = [int(part) for part in startDate.split("-")] if startDate else []
        startTimeParts = [int(part) for part in startTime.split(":")] if startTime else []
        endDateParts = [int(part) for part in endDate.split("-")] if endDate else []
        endTimeParts = [int(part) for part in endTime.split(":")] if endTime else []
        if len(startDateParts) != 3: error = "Start date not in yyyy-mm-dd format."
        elif len(startTimeParts) != 2: error = "Start time not in hh:mm format."
        elif len(endDateParts) != 3: error = "End date not in yyyy-mm-dd format."
        elif len(endTimeParts) != 2: error = "End time not in hh:mm format."
        #Process request if no errors
        if error is None:
            #Create Match and Project aggregate steps
            startTimestamp = datetime_to_nanoseconds_since_epoch(datetime(startDateParts[0], startDateParts[1], startDateParts[2], startTimeParts[0], startTimeParts[1], 0, 0))
            endTimestamp = datetime_to_nanoseconds_since_epoch(datetime(endDateParts[0], endDateParts[1], endDateParts[2], endTimeParts[0], endTimeParts[1], 59, 999999))
            match = {
                "population":population,
                "timestamp":{"$gte":startTimestamp, "$lte":endTimestamp}
            }
            if channels: match["channels.name"] = {"$in":channels}
            project = {
                "_id":0,
                "name":1,
                "timestamp":1
            }
            project["channels"] = {"$filter":{"input":"$channels", "as":"channel", "cond":{"$or":[{"$eq":["$$channel.name", channel]} for channel in channels]}}} if channels else 1
            #Query the database
            channel_x, channel_y, channel_value_sum = {}, {}, {}
            for document in default_collection().aggregate([
                {"$match":match},
                {"$project":project}
            ]):
                #Enumerate through channels
                for channel in document["channels"]:
                    if type(channel["value"]) == dict:
                        for key in channel["value"]:
                            name = (document["name"], channel["name"], key)
                            if name in channel_x:
                                channel_x[name].append(document["timestamp"])
                                channel_y[name].append(channel["value"][key])
                                channel_value_sum[name] += channel["value"][key]
                            else:
                                channel_colour[name] = colors.named.__all__[randint(0, len(colors.named.__all__) - 1)]
                                channel_x[name] = [document["timestamp"]]
                                channel_y[name] = [channel["value"][key]]
                                channel_value_sum[name] = channel["value"][key]
                    elif type(channel["value"]) == int or type(channel["value"]) == float:
                        name = (document["name"], channel["name"])
                        if name in channel_x:
                            channel_x[name].append(document["timestamp"])
                            channel_y[name].append(channel["value"])
                            channel_value_sum[name] += channel["value"]
                        else:
                            channel_colour[name] = colors.named.__all__[randint(0, len(colors.named.__all__) - 1)]
                            channel_x[name] = [document["timestamp"]]
                            channel_y[name] = [channel["value"]]
                            channel_value_sum[name] = channel["value"]
            #Calculate Statistical Data and Normalise
            calculate_statistical_analysis(channel_y, channel_value_sum, channel_mean, channel_median, channel_std, channel_skew, channel_kurtosis)
            #Create figure
            fig = figure(
                tools="pan,box_zoom,reset,save",
                output_backend="webgl",
                height=375,
                sizing_mode="scale_width",
                title="Population: {population} Channels: {channels}".format(
                    population=population,
                    channels=', '.join(channels) if channels else "All"
                ),
                x_axis_label="Time"
            )
            fig.toolbar.logo=None
            fig.toolbar.autohide=True
            for channel in channel_x:
                fig.line(channel_x[channel], channel_y[channel], line_color=channel_colour[channel])
            js, html=components(fig)
    #Render Template
    return render_template(
        "statistics.html", 
        error=error, 
        population=population, populations=populations, channels=channels, 
        scripts=js, figure=html, 
        key=channel_colour, mean=channel_mean, median=channel_median,
        std=channel_std, skew=channel_skew, kurtosis=channel_kurtosis
    )