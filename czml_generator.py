import pandas as pd
import numpy as np
import json
import datetime

def convertTimstamp2IsoDatetime(timestamp):
    dt_object = datetime.datetime.utcfromtimestamp(timestamp//1000.0)
    iso_datetime = dt_object.isoformat() + "Z"
    return iso_datetime

def convertTelemetries2DF(mission_path, starttime):
    lats = []
    lons = []
    heights = []
    starttimes = []
    stoptimes = []
    durations = []

    for point in mission_path:
        lats.append(point['latitude'])
        lons.append(point['longitude'])
        heights.append(point['height'])
        timestamp = point['timestamp']
        starttimes.append(convertTimstamp2IsoDatetime(starttime))
        stoptimes.append(convertTimstamp2IsoDatetime(timestamp))
        durations.append(1)
                   
    output = pd.DataFrame()
    output['latitude'] = lats
    output['longitude'] = lons
    output['height'] = heights
    output['starttime'] = starttimes
    output['stoptime'] = stoptimes
    output['duration'] = durations
    
    return output

def create_czml_path(df_input):
    results = []
    
    timestep = 0
    
    for i in df_input.index:
        results.append(timestep)
        results.append(df_input.longitude.ix[i])
        results.append(df_input.latitude.ix[i])
        results.append(df_input.height.ix[i])
        duration = df_input.duration.ix[(i)]
        timestep += duration
        
    return results

def point_with_trailing_path(df_input, time_multiplier = 1):
    
    # Store output in array
    czml_output = []

    # Define global variables
    global_id = "document"
    global_name = "Flight Logs Test"
    global_version = "1.0"
    global_author = "CuroUAV"
    global_starttime = str(min(df_input['starttime'])).replace(" ", "T")
    global_stoptime = str(max(df_input['stoptime'])).replace(" ", "T")
    global_availability = global_starttime + "/" + global_stoptime    
    
    # Create packet with global variables
    global_element = {
        "id" : global_id,
        "name" : global_name,
        "version" : global_version,
        "author": global_author,
        "clock": {
            "interval": global_availability,
            "currentTime": global_starttime,
            "multiplier": time_multiplier
        }
    }
    
    # Append global packet to output
    czml_output.append(global_element)
    
    # Define path variables
    path_id = "flight_log_id"
    path_starttime = str(min(df_input['starttime'])).replace(" ", "T")
    path_stoptime = str(max(df_input['stoptime'])).replace(" ", "T")
    path_availability = path_starttime + "/" + path_stoptime
    czml_path = create_czml_path(df)

    # Create path object
    path_object = {
      "id": path_id,

      "availability": path_availability,

      "path": {
        "material": {
          "polylineOutline": {
            "color": {
              "rgba": [255, 0, 255, 255],
            },
            "outlineColor": {
              "rgba": [0, 255, 255, 255],
            },
            "outlineWidth": 5,
          },
        },
        "width": 8,
        "leadTime": 10,
        "trailTime": 1000,
        "resolution": 5,
      },
      "billboard": {
        "image":
          "data:image/png;base64,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",
        "scale": 1.5,
        "eyeOffset": {
          "cartesian": [0.0, 0.0, -10.0],
        },
      },

      "position": {
        "epoch": path_starttime,
        "cartographicDegrees": czml_path,
      },
    }

    # Append path element to output
    czml_output.append(path_object)
    
    return czml_output

starttime = 1691035489166
path_points = [
  {"latitude": -33.929884, "longitude": 150.607225, "height": 162.0, "timestamp": 1691035489166},
  {"latitude": -33.929855, "longitude": 150.607269, "height": 163.0, "timestamp": 1691035491126},
  {"latitude": -33.929824, "longitude": 150.607292, "height":	163.4, "timestamp": 1691035493234},
	{"latitude": -33.929788, "longitude": 150.607308, "height":	163.4, "timestamp": 1691035495220},
	{"latitude": -33.929926, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035497281},
  {"latitude": -33.929836, "longitude": 150.607312, "height":	163.5, "timestamp": 1691035499153},
  {"latitude": -33.929846, "longitude": 150.607312, "height":	163.6, "timestamp": 1691035501263},
  {"latitude": -33.929856, "longitude": 150.607312, "height":	163.7, "timestamp": 1691035505221},
  {"latitude": -33.929866, "longitude": 150.607312, "height":	163.8, "timestamp": 1691035507145},
  {"latitude": -33.929876, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035509154},
  {"latitude": -33.929886, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035511152},
  {"latitude": -33.929896, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035513316},
  {"latitude": -33.929824, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035515138},
  {"latitude": -34.929788, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035517176},
  {"latitude": -35.929826, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035507876},
  {"latitude": -33.929788, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035519133},
  {"latitude": -33.929826, "longitude": 150.607312, "height":	0.4, "timestamp": 1691035521158},
  {"latitude": -33.929788, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035523135},
  {"latitude": -33.929826, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035525157},
  {"latitude": -33.929788, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035527153},
  {"latitude": -33.929826, "longitude": 150.607312, "height":	10.4, "timestamp": 1691035529288},
  {"latitude": -33.929788, "longitude": 150.607312, "height":	163.4, "timestamp": 1691035531138},
  {"latitude": -33.929788, "longitude": 150.607312, "height":	12.4, "timestamp": 1691035533145},
]
df = convertTelemetries2DF(path_points, starttime)
czml_output = point_with_trailing_path(df)

with open('./data/sample.czml', 'w') as outfile:
    json.dump(czml_output, outfile)

print('>>>Generation success!!!')
