# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    genotype.py
#       Represents one rider on MBTA.
#    Fall 2023
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import json 
import requests
import random
import pandas as pd

class Time:
    def __init__(self, text, text_range, start, duration):
        self.text = text
        self.text_range = text_range
        self.start = start
        self.duration = duration # hours

times = [
    Time("VERY_EARLY_MORNING","3am-5:59am",300,3),
    Time("EARLY_AM","6am-6:59am",600,1),
    Time("AM_PEAK","7am-8:59am",700,2),
    Time("MIDDAY_BASE","9am-1:29pm",900,4.5),
    Time("MIDDAY_SCHOOL","1:30pm-3:59pm",1330,2.5),
    Time("PM_PEAK","4pm-6:29pm",1600,2.5),
    Time("EVENING","6:30pm-9:59pm",1830,3.5),
    Time("LATE_EVENING","10pm-11:59pm",2200,2),
    Time("NIGHT","12am-2:59am",0,3)
]

df = pd.read_csv('MBTA_stops.csv')

class Ride:
    # Initialize a random ride
    # modality should be either 'rail' or 'bus'
    def __init__(self, modality):
        # select random start/end station
        # TODO weight based on ridership proportions, std deviation
        
        # select random start time
        # TODO weight similarly
        # get route/timing info
        p = {
            "mode":"transit", 
            "transit_mode":modality,
            "origins":,
            "destinations":,
            "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
        }
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
        # determine if we're more likely to arrive @ same start time, or in next time slot
        self.dict = {
            "start_point":,
            "end_point":,
            "start_time":random.choice(times),
            "end_time":,
            "route":,
        }

class Genotype:
    def __init__(self):
        # ~671000 rides on rail each day
        # ~77300 rides on bus each day