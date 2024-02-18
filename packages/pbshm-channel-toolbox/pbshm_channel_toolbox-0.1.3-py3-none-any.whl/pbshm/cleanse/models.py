from functools import wraps
from json import dumps as json_dumps, loads as json_loads
from time import time as time_seconds
from typing import List, Dict, Union

from bson.int64 import Int64
from bson.objectid import ObjectId

from pbshm.db import db_connect
from pbshm.cleanse.procedures import timestamps, channels, missing, statistics, sterilise

#Measure Metric Method Decorator
def measure_metric(key: str):
    def method_decorator(method):
        @wraps(method)
        def wrapped(instance, *args, **kwargs):
            start = time_seconds()
            result = method(instance, *args, **kwargs)
            end = time_seconds()
            if key in instance.metrics:
                instance.metrics.pop(key)
            instance.metrics[key] = AutoStatMetric(start, end, end - start)
            return result
        return wrapped
    return method_decorator

class AutoStatSource:
    def __init__(self, collection: str, population: str):
        self.collection = collection
        self.population = population
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["collection"],
            data["population"]
        )

class AutoStatMetric:
    def __init__(self, start: float, end: float, elapsed: float):
        self.start = start
        self.end = end
        self.elapsed = elapsed
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["start"],
            data["end"],
            data["elapsed"]
        )

class AutoStatCleanseChannel:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["name"],
            data["type"]
        )

class AutoStatCleanseDetails:
    def __init__(self, start_timestamp: Int64, end_timestamp: Int64, frequency: Int64, missing_timestamps: List[Int64], structures: List[str] = [], channels: List[AutoStatCleanseChannel] = []):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.frequency = frequency
        self.missing_timestamps = missing_timestamps
        self.structures = structures
        self.channels = channels
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["start_timestamp"],
            data["end_timestamp"],
            data["frequency"],
            [item for item in data["missing_timestamps"]],
            [item for item in data["structures"]],
            [AutoStatCleanseChannel.from_json(item) for item in data["channels"]]
        )

class AutoStatCleanseSelection:
    def __init__(self, structures: List[str] = [], channels: List[AutoStatCleanseChannel] = []):
        self.structures = structures
        self.channels = channels
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            [item for item in data["structures"]],
            [AutoStatCleanseChannel.from_json(item) for item in data["channels"]]
        )

class AutoStatCleanseSettings:
    def __init__(self, required: AutoStatCleanseSelection = AutoStatCleanseSelection(), included: AutoStatCleanseSelection = AutoStatCleanseSelection(), timestamps: List[Int64] = []):
        self.required = required
        self.included = included
        self.timestamps = timestamps
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            AutoStatCleanseSelection.from_json(data["required"]),
            AutoStatCleanseSelection.from_json(data["included"]),
            [item for item in data["timestamps"]]
        )

class AutoStatCleanseMissingStructureChannel:
    def __init__(self, name: str, channels: List[AutoStatCleanseChannel] = []):
        self.name = name
        self.channels = channels
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["name"],
            [item for item in data["channels"]]
        )

class AutoStatCleanseTimepoint:
    def __init__(self, timestamp: Int64, structures: List[str], channels: List[AutoStatCleanseMissingStructureChannel] = []):
        self.timestamp = timestamp
        self.structures = structures
        self.channels = channels
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["timestamp"],
            [item for item in data["structures"]],
            [AutoStatCleanseMissingStructureChannel.from_json(item) for item in data["channels"]]
        )

class AutoStatCleanseStatistic:
    def __init__(self, name: str, mean: Union[int, Int64, float, dict], std: Union[int, Int64, float, dict]):
        self.name = name
        self.mean = mean
        self.std = std
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            data["name"],
            data["mean"],
            data["std"]
        )

class AutoStatCleanseCalculations:
    def __init__(self, missing: List[AutoStatCleanseTimepoint] = [], statistics: List[AutoStatCleanseStatistic] = []):
        self.missing = missing
        self.statistics = statistics
    
    @classmethod
    def from_json(cls, data: {}):
        return cls(
            [AutoStatCleanseTimepoint.from_json(item) for item in data["missing"]],
            [AutoStatCleanseStatistic.from_json(item) for item in data["statistics"]]
        )

class AutoStatCleanse:
    def __init__(self, details: AutoStatCleanseDetails, settings: AutoStatCleanseSettings = AutoStatCleanseSettings(), calculations: AutoStatCleanseCalculations = AutoStatCleanseCalculations()):
        self.details = details
        self.settings = settings
        self.calculations = calculations
    
    @classmethod
    def from_json(cls, data: {}):
        return None if data == None else cls(
            AutoStatCleanseDetails.from_json(data["details"]),
            AutoStatCleanseSettings.from_json(data["settings"]),
            AutoStatCleanseCalculations.from_json(data["calculations"])
        )

class AutoStatRequest:
    collection = "automated-statistician"

    def __init__(self, input: AutoStatSource, output: AutoStatSource, metrics: Dict[str, AutoStatMetric] = {}, cleanse: AutoStatCleanse = None):
        self._id = None
        self.input = input
        self.output = output
        self.metrics = metrics
        self.cleanse = cleanse

    #Discover Timestamps
    @measure_metric("cleanse-timestamps")
    def discover_timestamps(self):
        data = timestamps(self.input.population)
        self.cleanse = AutoStatCleanse(
            AutoStatCleanseDetails(
                data["start_timestamp"],
                data["end_timestamp"],
                data["frequency"],
                data["missing_timestamps"]
            )
        )
    
    #Discover Structures & Channels
    @measure_metric("cleanse-structures-channels")
    def discover_structures_channels(self):
        data = channels(self.input.population)
        self.cleanse.details.structures = data["structures"]
        self.cleanse.settings.required.structures = data["structures"]
        self.cleanse.settings.included.structures = data["structures"]
        self.cleanse.details.channels = [
            AutoStatCleanseChannel(
                channel["name"],
                channel["type"]
            )
            for channel in data["channels"]
        ]
        self.cleanse.settings.required.channels = [
            AutoStatCleanseChannel(
                channel["name"],
                channel["type"]
            )
            for channel in data["channels"]
        ]
        self.cleanse.settings.included.channels = [
            AutoStatCleanseChannel(
                channel["name"],
                channel["type"]
            )
            for channel in data["channels"]
        ]
    
    #Discover Missing
    @measure_metric("cleanse-missing")
    def discover_missing(self):
        data = missing(
            self.input.population,
            self.cleanse.settings.required.structures,
            [channel.__dict__ for channel in self.cleanse.settings.required.channels]
        )
        self.cleanse.settings.timestamps = [timepoint["timestamp"] for timepoint in data]
        self.cleanse.calculations.missing = [
            AutoStatCleanseTimepoint(
                timepoint["timestamp"],
                timepoint["structures"],
                [
                    AutoStatCleanseMissingStructureChannel(
                        structure_channel["name"],
                        [
                            AutoStatCleanseChannel(
                                channel["name"],
                                channel["type"]
                            )
                            for channel in structure_channel["channels"]
                        ]
                    )
                    for structure_channel in timepoint["channels"]
                ]
            )
            for timepoint in data
        ]
    
    #Generate Statistics
    @measure_metric("cleanse-statistics")
    def generate_statistics(self):
        data = statistics(
            self.input.population,
            self.cleanse.settings.timestamps,
            self.cleanse.settings.included.structures,
            [channel.__dict__ for channel in self.cleanse.settings.included.channels]
        )
        self.cleanse.calculations.statistics = [
            AutoStatCleanseStatistic(
                statistic["name"],
                statistic["mean"],
                statistic["std"]
            )
            for statistic in data
        ]

    #Process Sterilisation
    @measure_metric("cleanse-sterilise")
    def process_sterilisation(self):
        sterilise(
            self.input.population,
            self.cleanse.settings.timestamps,
            self.cleanse.settings.included.structures,
            [channel.__dict__ for channel in self.cleanse.settings.included.channels],
            [statistic.__dict__ for statistic in self.cleanse.calculations.statistics],
            self.output.collection
        )

    #Convert to JSON
    def to_json(self) -> str:
        return json_dumps(self, default = lambda item: item.__dict__)

    #Save to Database
    def save(self):
        save_dict = json_loads(self.to_json())
        save_dict.pop("_id", {})
        if self._id is not None:
            db_connect()[self.collection].replace_one({"_id": ObjectId(self._id)}, save_dict)
        else:
            result = db_connect()[self.collection].insert_one(save_dict)
            self._id = str(result.inserted_id)
    
    @classmethod
    def from_json(cls, data: {}):
        instance = cls(
            AutoStatSource.from_json(data["input"]),
            AutoStatSource.from_json(data["output"]),
            {key:AutoStatMetric.from_json(data["metrics"][key]) for key in data["metrics"]},
            AutoStatCleanse.from_json(data["cleanse"])
        )
        instance._id = str(data["_id"])
        return instance

    @classmethod
    def load(cls, request_id: str):
        return cls.from_json(db_connect()[cls.collection].find_one({"_id": ObjectId(request_id)}))
