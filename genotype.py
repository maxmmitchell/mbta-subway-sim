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
    def __init__(self, text, text_range, start, duration, odds_rail, odds_bus):
        self.text = text
        self.text_range = text_range
        self.start = start
        self.duration = duration # hours
        self.odds_rail = odds_rail
        self.odds_bus = odds_bus

times = [
    # id, text, time, duration, odds_rail, odds_bus (calculated using 2019 data)
    Time("VERY_EARLY_MORNING","3am-5:59am",300,3,0.013945182241395501,0.06682732111944974),
    Time("EARLY_AM","6am-6:59am",600,1,0.04850329660828721,0.1551210877786039),
    Time("AM_PEAK","7am-8:59am",700,2,0.1931098427198099,0.1708102019470824),
    Time("MIDDAY_BASE","9am-1:29pm",900,4.5,0.18468012539484022,0.11265796173882053),
    Time("MIDDAY_SCHOOL","1:30pm-3:59pm",1330,2.5,0.13960536103189877,0.19537424182261517),
    Time("PM_PEAK","4pm-6:29pm",1600,2.5,0.24809902793657512,0.15503673770243018),
    Time("EVENING","6:30pm-9:59pm",1830,3.5,0.12979677747782262,0.08679233530324226),
    Time("LATE_EVENING","10pm-11:59pm",2200,2,0.036803057654496374,0.04038162569848716),
    Time("NIGHT","12am-2:59am",0,3,0.005457328934874285,0.016998486889404713)
]

df_rail_ridership = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
df_bus_ridership = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')
df_bus_stops = pd.read_csv('MBTA_Bus_Stops.csv')

class Ride:
    def pick_station(time, modality, dir):
        df = df_rail_ridership if modality == 'rail' else df_bus_ridership
        selected = df.sample(1)
        seed = random.random()
        odds = 0
        for index, row in df[['time_period_name' == time]]:
            odds += row['odds_on' if dir == 'on' else 'odds_off']
            if seed <= odds:
                selected = row
        return selected
    # Initialize a random ride
    # modality should be either 'rail' or 'bus'
    def __init__(self, modality):
        # select pseudo-random start time, weighted based on ridership proportions
        selected_time = times[0]
        time_seed = random.random()
        time_odds = 0
        for t in times:
            time_odds += t.odds_rail if modality == 'rail' else t.odds_bus
            if time_seed <= time_odds:
                selected_time = t
        # select random start/end station, weighted based on ridership proportions
        selected_start = pick_station(selected_time.text, modality, 'on')
        selected_end = pick_station(selected_time.text, modality, 'off')
        # get route/timing info
        p = {
            "mode":"transit", 
            "transit_mode":modality,
            "origins":o_lat + ', ' + o_lon,
            "destinations":d_lat + ', ' + d_lon,
            "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
        }
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
        # determine if we're more likely to arrive @ same start time, or in next time slot
        self.dict = {
            "start_point":,
            "end_point":,
            "start_time":selected_time,
            "end_time":,
            "route":,
        }

class Genotype:
    def __init__(self):
        # ~671000 rides on rail each day
        # ~77300 rides on bus each day