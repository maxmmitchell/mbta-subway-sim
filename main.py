###############################################################
#    main.py
#        MVP for project. Predict impact of outages at basic
#        capacity.
#    Fall 2023
#    maxwell.mitchell@tufts.edu
#    Master's Capstone Project
###############################################################

import json 
# TODO:
# - alternate station generator -> find nearest stations in walking distance from target station
#       -> evaluate partial vs. true substitutes (true substitute reaches the same stations in similar times) 
# - evaluator
#       -> How many affected? Where will they go? Impact on other stations? Arrival time impact? 
#       -> riders walk to nearest substitute; assume random distribution within 20 min walk of station
# - advanced options
#       -> Graphing/comparisons
#       -> express behavior vs. line splittage (partial vs. full outage)
#       -> complex, multi-stop outages
# - stop adder
#       -> take lat/lon for new stop
#       -> anticipate ridership based on riders extant it will attract
#       -> show anticipated impact on nearby stations
#       -> ability to compare multiple

# command control, take user input, station and time range
f = open("station-data.json")
stations_codes = json.load(f)
user_station = ''
outages = [] # list, extensible to having multiple TODO enable that feature

def validate_station(s, outages):
    for station in stations_codes:
        if s.lower() in station["station_complex"].lower():
            if input("Did you mean '" + station["station_complex"] + "' ? (y/n)    ") == "y":
                outages.append([station["station_complex"], station["station_complex_id"]])
                return True
    print("Could not find '" + s + "' in 'stations-codes.json'.")
    return False

user_station = input("Please select a valid station:    ")
while (not validate_station(user_station, outages)):
    user_station = input("Please select a valid station:    ")

user_time = ''
def validate_time(s, outages):
    days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    times = s.split("/")
    timestamps = []
    for t in times:
        data = t.split(":")
        if not data[0].lower() in days:
            print(data[0] + " not a valid day of week.")
            return False
        if len(data[1]) == 2 and not (int(data[1]) >= 0 and int(data[1]) <= 23):
            print(data[1] + " not a valid hour. Please give an hour from 0 to 23.")
            return False
        timestamps.append("2023-10-0" + str(days.index(data[0].lower()) + 1) + "T" + (data[1]) + ":00:00.000")
    outages[-1].append(timestamps)
    return True
    

user_time = input("Time format: DAY_OF_WEEK:TIME\nTime range format: START_TIME/END_TIME\nExample: Monday:01/Wednesday:22\nTimes will be rounded down to nearest hour.\nPlease select a time range:    ")
while (not validate_time(user_time, outages)):
    user_time = input("Please select a time range:    ")

print("\n$ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $")
print("$")
print("$    Selected outage at: " + outages[-1][0] + ", code: " + outages[-1][1])
print("$    Internal simulated range " + outages[-1][2][0] + " to " + outages[-1][2][1])
print("$")
print("$ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $\n")

# alternate station generator
# TODO find all stations within certain distance of station -> alt stations
# get location of outage station
code = outages[-1][1]
# TODO calculate alt station substitutability -> true vs. partial subs
# TODO distribute riders across range to alt stations -- how do we distribute? 

