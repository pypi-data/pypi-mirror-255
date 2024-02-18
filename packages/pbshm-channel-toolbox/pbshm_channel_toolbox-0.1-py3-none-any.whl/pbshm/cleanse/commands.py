import click
from flask import Blueprint, current_app

from pbshm.cleanse.models import *

#Create Cleanse cli Blueprint
bp = Blueprint("cleanse-cli", __name__, cli_group="cleanse")

#Quick Create
@bp.cli.command("quick-create")
@click.argument("origin")
@click.option("--destination")
def command_quick_create(origin: str, destination: str = None):
    if destination is None:
        destination = origin + "-quick-create"
    print("Creating Auto Processing for: {population}".format(population=origin))
    request = AutoStatRequest(
        AutoStatSource(current_app.config["STRUCTURE_COLLECTION"], origin),
        AutoStatSource(destination, origin)
    )
    request.save()
    print("Created Request: {request_id}".format(request_id=request._id))

#Continue
@bp.cli.command("continue")
@click.argument("request-id")
@click.option("--stages", type=int, default=1)
def command_continue(request_id: str, stages: int):
    request = AutoStatRequest.load(request_id)
    print("Continuing with Request: {request_id}".format(request_id=request_id))
    for i in range(stages):
        if "cleanse-timestamps" not in request.metrics:
            print("Starting timestamp discovery on {collection}.{population}".format(collection=request.input.collection, population=request.input.population))
            request.discover_timestamps()
            print("Completed timestamp discovery: {time:.4f}s".format(time=request.metrics["cleanse-timestamps"].elapsed))
        elif "cleanse-structures-channels" not in request.metrics:
            print("Starting structures and channels discovery on {collection}.{population}".format(collection=request.input.collection, population=request.input.population))
            request.discover_structures_channels()
            print("Completed structures and channels discovery: {time:.4f}s".format(time=request.metrics["cleanse-structures-channels"].elapsed))
        elif "cleanse-missing" not in request.metrics:
            print("Starting missing data discovery on {collection}.{population} based upon the required selection".format(collection=request.input.collection, population=request.input.population))
            request.discover_missing()
            print("Completed missing data discovery: {time:.4f}s".format(time=request.metrics["cleanse-missing"].elapsed))
        elif "cleanse-statistics" not in request.metrics:
            print("Starting statistical calculation on {collection}.{population} with the included selection".format(collection=request.input.collection, population=request.input.population))
            request.generate_statistics()
            print("Completed statistical calculation: {time:.4f}s".format(time=request.metrics["cleanse-statistics"].elapsed))
        elif "cleanse-sterilise" not in request.metrics:
            print("Starting sterilisation on {collection}.{population} with the included selection".format(collection=request.input.collection, population=request.input.population))
            request.process_sterilisation()
            print("Completed sterilisation: {time:.4f}s".format(time=request.metrics["cleanse-sterilise"].elapsed))
        else:
            print("No next stage found on {collection}.{population}".format(collection=request.input.collection, population=request.input.population))
            break
        request.save()