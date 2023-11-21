###############################################################
#    getdata.py
#        A quick and dirty way to snag some data
#        using SOQL and HTTP gets.
#    Fall 2023
#    maxwell.mitchell@tufts.edu
#    Master's Capstone Project
###############################################################

import requests
import json

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# p = {   
#         "$select": "station_complex_id, station_complex, latitude, longitude, borough, routes where transit_timestamp = '2023-10-01T00:00:00.000' and payment_method = 'omny' limit 140000" # should be roughly 7 days worth
#     }
# response = requests.get("https://data.ny.gov/resource/wujg-7c2s.json", params = p)
# # print(response.status_code) # for debugging
# jprint(response.json())

f = open("station-data.json")
station_data = json.load(f)
for outage in station_data:
    alt_stations = {} 
    o_routes = outage["routes"].split(",")
    for station in station_data:
        if station["station_complex_id"] == outage["station_complex_id"]:
            continue
        if not any(r in station["routes"] for r in o_routes):
            continue
        p = {
            "mode":"walking", # TODO could eventually consider allowing the use of bus to get to/from subway
            "origins":outage["latitude"] + "," + outage["longitude"],
            "destinations":station["latitude"] + "," + station["longitude"],
            "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
        }
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
        walking_duration = response.json()["rows"][0]["elements"][0]["duration"]["value"] 
        if int(walking_duration) <= 1800:
            for r in o_routes:
                if r in station["routes"]:
                    if r in alt_stations:
                        # key already exists, we must compare
                        if walking_duration < alt_stations[r]["duration"]["value"]:
                            alt_stations[r] = {"id":station["station_complex_id"], "duration":response.json()["rows"][0]["elements"][0]["duration"]}
                    else:
                        alt_stations[r] = {"id":station["station_complex_id"], "duration":response.json()["rows"][0]["elements"][0]["duration"]}
    jprint(alt_stations)

            # 30 min walk, could be used in place of other station
            #print(response.json())