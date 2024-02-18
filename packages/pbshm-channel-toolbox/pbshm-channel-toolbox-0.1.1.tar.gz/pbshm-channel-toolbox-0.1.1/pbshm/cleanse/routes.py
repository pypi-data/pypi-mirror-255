from json import loads as json_loads
from urllib.parse import unquote_plus

from flask import Blueprint, jsonify, request, render_template

from pbshm.authentication import authenticate_request
from pbshm.autostat import population_list
from pbshm.cleanse.procedures import timestamps, channels, missing, statistics, sterilise

#Create the Cleanse Blueprint
bp = Blueprint(
    "cleanse",
    __name__,
    template_folder = "templates"
)

#Timestamp JSON View
@bp.route("/populations/<population>/timestamps")
@authenticate_request("autostat-cleanse")
def route_timestamps(population):
    return jsonify(timestamps(population=population))

#Structures Channels JSON View
@bp.route("/populations/<population>/channels")
@authenticate_request("autostat-cleanse")
def route_channels(population):
    return jsonify(channels(population=population))

#Missing JSON View
@bp.route("/populations/<population>/missing", methods=("GET", "POST"))
@authenticate_request("autostat-cleanse")
def route_missing(population):
    #Load Structures & Channels
    structures, channels = [], []
    if request.method == "POST" and request.json:
        structures = request.json["structures"] if "structures" in request.json else []
        channels = request.json["channels"] if "channels" in request.json else []
    elif request.method == "GET" and request.args.get("data"):
        data = json_loads(unquote_plus(request.args.get("data")))
        structures = data["structures"] if "structures" in data else []
        channels = data["channels"] if "channels" in data else []
    return jsonify(missing(population=population, structures=structures, channels=channels))

#Statistics JSON View
@bp.route("/populations/<population>/statistics", methods=("GET", "POST"))
@authenticate_request("autostat-cleanse")
def route_statistics(population):
    #Get Timestamps, Structures and Channels
    timestamps, structures, channels = [], [], []
    if request.method == "POST" and request.json:
        timestamps = request.json["timestamps"] if "timestamps" in request.json else []
        structures = request.json["structures"] if "structures" in request.json else []
        channels = request.json["channels"] if "channels" in request.json else []
    elif request.method == "GET" and request.args.get("data"):
        data = json_loads(unquote_plus(request.args.get("data")))
        timestamps = data["timestamps"] if "timestamps" in data else []
        structures = data["structures"] if "structures" in data else []
        channels = data["channels"] if "channels" in data else []
    return jsonify(statistics(population=population, timestamps=timestamps, structures=structures, channels=channels))

#Sterilise JSON View
@bp.route("/populations/<population>/sterilise/<destination>", methods=("GET", "POST"))
@authenticate_request("autostat-cleanse")
def route_sterilise(population, destination):
    #Get Timestamps, Structures, Channels and Statistics
    timestamps, structures, channels, statistics = [], [], [], []
    if request.method == "POST" and request.json:
        timestamps = request.json["timestamps"] if "timestamps" in request.json else []
        structures = request.json["structures"] if "structures" in request.json else []
        channels = request.json["channels"] if "channels" in request.json else []
        statistics = request.json["statistics"] if "statistics" in request.json else []
    elif request.method == "GET" and request.args.get("data"):
        data = json_loads(unquote_plus(request.args.get("data")))
        timestamps = data["timestamps"] if "timestamps" in data else []
        structures = data["structures"] if "structures" in data else []
        channels = data["channels"] if "channels" in data else []
        statistics = data["statistics"] if "statistics" in data else []
    return jsonify(sterilise(population=population, timestamps=timestamps, structures=structures, channels=channels, statistics=statistics, destination=destination))

#List View
@bp.route("/populations")
@authenticate_request("autostat-cleanse")
def route_list():
    return population_list("cleanse", "cleanse.route_details")

#Details View
@bp.route("/populations/<population>")
@authenticate_request("autostat-cleanse")
def route_details(population):
    return render_template("details.html", population=population)
