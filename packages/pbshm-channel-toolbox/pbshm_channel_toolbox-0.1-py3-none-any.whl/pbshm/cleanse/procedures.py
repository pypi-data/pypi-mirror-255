from pbshm.db import default_collection
from pbshm.mechanic import create_new_structure_collection

#Timestamp
def timestamps(population):
    documents = []
    for document in default_collection().aggregate([
        {"$match":{#Select the population documents with channels
            "population":population,
            "channels":{"$exists":True}
        }},
        {"$group":{#Generate a unique list of timestamps
            "_id":None,
            "timestamps":{"$addToSet":"$timestamp"}
        }},
        {"$unwind":"$timestamps"},#Seperate each timestamp into its own document
        {"$sort":{"timestamps":1}},#Sort via timestamps
        {"$group":{#Generate a list of ordered timestamps
            "_id":None,
            "start_timestamp":{"$first":"$timestamps"},
            "end_timestamp":{"$last":"$timestamps"},
            "timestamps":{"$push":"$timestamps"}
        }},
        {"$project":{#Calculate the delta between timestamp n and n-1
            "_id":0,
            "start_timestamp":1,
            "end_timestamp":1,
            "original_timestamps":"$timestamps",
            "timestamps":{
                "$reduce":{
                    "input":"$timestamps",
                    "initialValue":[],
                    "in":{
                        "$concatArrays":["$$value",[{
                            "$subtract":["$$this",{
                                "$cond":[
                                    {"$gt":[{"$size":"$$value"},0]},
                                    {"$arrayElemAt":["$timestamps",{"$subtract":[{"$size":"$$value"},1]}]},
                                    "$start_timestamp"
                                ]
                            }]
                        }]]
                    }
                }
            }
        }},
        {"$unwind":"$timestamps"},#Seperate each delta into its own document
        {"$group":{#Count the number of occurances for each delta value
            "_id":"$timestamps",
            "start_timestamp":{"$first":"$start_timestamp"},
            "end_timestamp":{"$last":"$end_timestamp"},
            "original_timestamps":{"$first":"$original_timestamps"},
            "count":{"$sum":1}
        }},
        {"$sort":{"count":-1}},#Sort via the count
        {"$limit":1},#First result only
        {"$project":{#Rename the delta value to frequency and calculate missing timestamps
            "_id":0,
            "start_timestamp":1,
            "end_timestamp":1,
            "frequency":"$_id",
            "missing_timestamps":{
                "$setDifference":[{
                    "$reduce":{
                        "input":{"$range":[1,{"$add":[{"$divide":[{"$subtract":["$end_timestamp","$start_timestamp"]},"$_id"]},1]},1]},
                        "initialValue":["$start_timestamp"],
                        "in":{"$concatArrays":["$$value",[{"$add":["$start_timestamp",{"$multiply":["$$this","$_id"]}]}]]}
                    }
                },"$original_timestamps"]
            }
        }}
    ]):
        documents.append(document)
    return documents[0] if len(documents) > 0 else {}

#Channels
def channels(population):
    documents = []
    for document in default_collection().aggregate([
        {"$match":{"population":population}},#Select the population
        {"$project":{#Keep only the name, channel name and channel type
            "_id":0,
            "name":1,
            "channels.name":1,
            "channels.type":1
        }},
        {"$group":{#Generate a list of structures and channels
            "_id":None,
            "structures":{"$addToSet":"$name"},
            "channels":{"$addToSet":"$channels"}
        }},
        {"$project":{#Reduce the channels from multiple arrays down to one unique channel array
            "_id":0,
            "structures":1,
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
        {"$unwind":"$channels"},#Seperate channels out into their own documents
        {"$sort":{"channels.name":1}},#Sort the channels by name
        {"$group":{#Bring all the documents back together
            "_id":None,
            "structures":{"$first":"$structures"},
            "channels":{"$push":"$channels"}
        }},
        {"$unwind":"$structures"},#Seperate structures out into their own documents
        {"$sort":{"structures":1}},#Sort the structures by name
        {"$group":{#Bring all the documents back together
            "_id":None,
            "structures":{"$push":"$structures"},
            "channels":{"$first":"$channels"}
        }},
        {"$project":{"_id":0}},#Remove the id
        {"$limit":1}#Return only 1 document
    ]):
        documents.append(document)
    return documents[0] if len(documents) > 0 else {}

#Missing
def missing(population, structures, channels):
    #Calculate Missing
    documents = []
    for document in default_collection().aggregate([
        {"$match":{"population":population}},#Select the Population
        {"$project":{#Keep only the timestamp, name channel name and channel type fields
            "_id":0,
            "timestamp":1,
            "name":1,
            "channels.name":1,
            "channels.type":1,
        }},
        {"$group":{#Generate a list of channels for each timestamp/name
            "_id":{
                "timestamp":"$timestamp",
                "name":"$name"
            },
            "channels":{
                "$addToSet":"$channels"
            }
        }},
        {"$project":{#Reduce the channels from multiple arrays down to one unique channel array
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
        {"$project":{#Generate a list of channels that are missing for each timestamp/name compared to the channels available within the population
            "timestamp":"$_id.timestamp",
            "name":"$_id.name",
            "channels":{
                "$setDifference":[channels,"$channels"]
            }
        }},
        {"$group":{#Generate a list of structures (with assosiated missing channels) for each timestamp
            "_id":"$timestamp",
            "structures":{
                "$addToSet":{
                    "name":"$name",
                    "channels":"$channels",
                    "count":{"$size":"$channels"}
                }
            }
        }},
        {"$project":{#Generate a list of structures that are missing for each timestamp compared to the structures available within the population
            "structures":1,
            "missing_structures":{
                "$setDifference":[structures,"$structures.name"]
            }
        }},
        {"$project":{#Calculate the size of missing structures for each timestamp
            "_id":0,
            "timestamp":"$_id",
            "structures":1,
            "missing_structures":1,
            "missing_structures_count":{"$size":"$missing_structures"}
        }},
        {"$match":{#Keep only documents that have missing structures or missing channels
            "$or":[{"missing_structures_count":{"$gt":0}},{"structures.count":{"$gt":0}}]
        }},
        {"$project":{#Keep only structures (with assosiated missing channels) that have missing channels
            "timestamp":1,
            "missing_structures":1,
            "missing_channels":{
                "$filter":{
                    "input":"$structures","as":"structure","cond":{"$gt":["$$structure.count", 0]}
                }
            }
        }},
        {"$project":{#Remove the channel count
            "timestamp":1,
            "missing_structures":1,
            "missing_channels.name":1,
            "missing_channels.channels":1
        }},
        {"$project":{#Rename the fields
            "timestamp":1,
            "structures":"$missing_structures",
            "channels":"$missing_channels"
        }},
        {"$sort":{"timestamp":1}}#Sort via timestamp
    ], allowDiskUse = True):
        documents.append(document)
    return documents

#Statistics
def statistics(population, timestamps, structures, channels):
    #Generate Mean and Standard Deviation per channels
    documents = []
    for document in default_collection().aggregate([
        {"$match":{#Select the population and structures and exclude document in the timestamp list
            "population":population,
            "timestamp":{"$nin":timestamps},
            "name":{"$in":structures}
        }},
        {"$project":{#Keep only the channels required and remove any text based channels
            "name":1,
            "channels":{
                "$filter":{
                    "input":"$channels","as":"channel","cond":{"$and":[{"$in":[{"name":"$$channel.name","type":"$$channel.type"},channels]},{"$ne":["$$channel.type","text"]}]}
                }
            }
        }},
        {"$project":{#Keep only the channel name and value
            "_id":0,
            "channels.name":1,
            "channels.value":1
        }},
        {"$unwind":"$channels"},#Seperate channels out into their own documents
        {"$group":{#Calculate the mean and standard deviation for each channel
            "_id":"$channels.name",
            "mean":{
                "$avg":{"$cond":[{"$ne":[{"$type":"$channels.value"},"object"]},"$channels.value",None]}
            },
            "std":{
                "$stdDevPop":{"$cond":[{"$ne":[{"$type":"$channels.value"},"object"]},"$channels.value",None]}
            },
            "min_mean":{
                "$avg":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.min",None]}
            },
            "min_std":{
                "$stdDevPop":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.min",None]}
            },
            "max_mean":{
                "$avg":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.max",None]}
            },
            "max_std":{
                "$stdDevPop":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.max",None]}
            },
            "mean_mean":{
                "$avg":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.mean",None]}
            },
            "mean_std":{
                "$stdDevPop":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.mean",None]}
            },
            "std_mean":{
                "$avg":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.std",None]}
            },
            "std_std":{
                "$stdDevPop":{"$cond":[{"$eq":[{"$type":"$channels.value"},"object"]},"$channels.value.std",None]}
            }
        }},
        {"$project":{#Create a mean and standard deviation object for each channel
            "_id":0,
            "name":"$_id",
            "mean":{
                "$ifNull":["$mean",{
                    "min":"$min_mean",
                    "max":"$max_mean",
                    "mean":"$mean_mean",
                    "std":"$std_mean"
                }]
            },
            "std":{
                "$ifNull":["$std",{
                    "min":"$min_std",
                    "max":"$max_std",
                    "mean":"$mean_std",
                    "std":"$std_std"
                }]
            }
        }},
        {"$sort":{"name":1}}#Order the results by channel name
    ], allowDiskUse = True):
        documents.append(document)
    return documents

#Sterilise
def sterilise(population, timestamps, structures, channels, statistics, destination):
    #Create output collection
    create_new_structure_collection(destination)
    #Sterilise data into destination
    default_collection().aggregate([
        {"$match":{#Select the population and structures whilst excluding the timestamps
            "population":population,
            "timestamp":{"$nin":timestamps},
            "name":{"$in":structures}
        }},
        {"$project":{#Filter out unrequired channels
            "name":1,
            "timestamp":1,
            "population":1,
            "channels":{
                "$filter":{
                    "input":"$channels","as":"channel","cond":{"$in":[{"name":"$$channel.name","type":"$$channel.type"},channels]}
                }
            }
        }},
        {"$unwind":"$channels"},#Seperate channels out into their own documents
        {"$addFields":{#Add the corrseponding normalisation data to each channel
            "normalisation":{
                "$arrayElemAt":[{
                    "$reduce":{
                        "input":statistics,
                        "initialValue":[],
                        "in":{"$concatArrays":["$$value",{"$cond":[{"$eq":["$$this.name","$channels.name"]},[{"mean":"$$this.mean","std":"$$this.std"}],[]]}]}
                    }
                },0]
            }
        }},
        {"$project":{#Normalise each channel: (value-mean)/std
            "name":1,
            "timestamp":1,
            "population":{"$concat":["$population","-normalised"]},
            "channels.name":1,
            "channels.type":1,
            "channels.unit":1,
            "channels.value":{
                "$cond":[
                    {"$or":[{"$eq":["$channels.type","date"]},{"$eq":["$channels.type","text"]}]},"$channels.value",
                    {
                        "$cond":[
                            {"$ne":[{"$type":"$channels.value"},"object"]},
                            {"$cond":[{"$ne":["$normalisation.std",0]},{"$divide":[{"$subtract":["$channels.value","$normalisation.mean"]},"$normalisation.std"]},{"$cond":[{"$eq":["$channels.type","double"]},0.0,0]}]},
                            {
                                "min":{"$cond":[{"$ne":[{"$type":"$channels.value.min"},"null"]},{"$cond":[{"$ne":["$normalisation.std.min",0]},{"$divide":[{"$subtract":["$channels.value.min","$normalisation.mean.min"]},"$normalisation.std.min"]},0]},None]},
                                "max":{"$cond":[{"$ne":[{"$type":"$channels.value.max"},"null"]},{"$cond":[{"$ne":["$normalisation.std.max",0]},{"$divide":[{"$subtract":["$channels.value.max","$normalisation.mean.max"]},"$normalisation.std.max"]},0]},None]},
                                "mean":{"$cond":[{"$ne":[{"$type":"$channels.value.mean"},"null"]},{"$cond":[{"$ne":["$normalisation.std.mean",0]},{"$divide":[{"$subtract":["$channels.value.mean","$normalisation.mean.mean"]},"$normalisation.std.mean"]},0]},None]},
                                "std":{"$cond":[{"$ne":[{"$type":"$channels.value.std"},"null"]},{"$cond":[{"$ne":["$normalisation.std.std",0]},{"$divide":[{"$subtract":["$channels.value.std","$normalisation.mean.std"]},"$normalisation.std.std"]},0]},None]},
                            }
                        ]
                    }
                ]
            }
        }},
        {"$sort":{"channels.name":1}},#Sort the channels by name
        {"$group":{#Group all of the document back together by the original document id
            "_id":"$_id",
            "name":{"$first":"$name"},
            "population":{"$first":"$population"},
            "timestamp":{"$first":"$timestamp"},
            "channels":{
                "$push":"$channels"
            }
        }},
        {"$project":{#Rename the original document id to origin
            "_id":0,
            "origin":"$_id",
            "name":1,
            "population":1,
            "timestamp":1,
            "channels":1
        }},
        {"$out":destination}#Output to the destination collection
    ], allowDiskUse = True)
    return True