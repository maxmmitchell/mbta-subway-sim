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
        self.duration = duration # minutes of OPERATING hours, e.g. 5am - 1am
        self.odds_rail = odds_rail
        self.odds_bus = odds_bus

times = [
    # id, text, time, duration, odds_rail, odds_bus (calculated using 2019 data)
    Time("VERY_EARLY_MORNING","3am-5:59am",300,59,0.013945182241395501,0.06682732111944974),
    Time("EARLY_AM","6am-6:59am",600,59,0.04850329660828721,0.1551210877786039),
    Time("AM_PEAK","7am-8:59am",700,119,0.1931098427198099,0.1708102019470824),
    Time("MIDDAY_BASE","9am-1:29pm",900,269,0.18468012539484022,0.11265796173882053),
    Time("MIDDAY_SCHOOL","1:30pm-3:59pm",1330,149,0.13960536103189877,0.19537424182261517),
    Time("PM_PEAK","4pm-6:29pm",1600,149,0.24809902793657512,0.15503673770243018),
    Time("EVENING","6:30pm-9:59pm",1830,209,0.12979677747782262,0.08679233530324226),
    Time("LATE_EVENING","10pm-11:59pm",2200,119,0.036803057654496374,0.04038162569848716),
    Time("NIGHT","12am-2:59am",0,59,0.005457328934874285,0.016998486889404713)
]

df_rail_ridership = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
df_bus_ridership = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')
df_bus_stops = pd.read_csv('MBTA_Bus_Stops.csv')

class Ride:
    def pick_station(self, time, modality, dir):
        df = df_rail_ridership if modality == 'rail' else df_bus_ridership
        selected = df.sample(1)
        seed = random.random()
        odds = 0
        for index, row in df[df.time_period_name == time].iterrows():
            odds += row['odds_on' if dir == 'on' else 'odds_off']
            if seed <= odds:
                selected = row
                break
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
                break
        # select random start/end station, weighted based on ridership proportions
        selected_start = self.pick_station(selected_time.text, modality, 'on')
        # TODO incorporate direction here???? the odds of the start at this time
        # is associated with a direction (0 or 1), and that should be used to limit the possible
        # end stations, for further accuracy/consistency with the data! Do we need each station to
        # know all possible reachable stations given its current direction? an option, which could hasten
        # the station selection process and give us what we want here...
        selected_end = self.pick_station(selected_time.text, modality, 'off')
        # ensure end is different from start
        while selected_end['stop_id'] == selected_start['stop_id']:
            selected_end = self.pick_station(selected_time.text, modality, 'off')
        # get coordinates
        #print(selected_start['stop_name'] + ', ' + str(selected_start['stop_id']))
        #print(selected_end['stop_name'] + ', ' + str(selected_end['stop_id']))
        df = df_rail_stops if modality == 'rail' else df_bus_stops
        o_lat = ""
        o_lon = ""
        d_lat = ""
        d_lon = ""
        for index, row in df.iterrows():
            if str(selected_start['stop_id']) == str(row['stop_id']):
                o_lat = str(row['stop_lat'])
                o_lon = str(row['stop_lon'])
            if str(selected_end['stop_id']) == str(row['stop_id']):
                d_lat = str(row['stop_lat'])
                d_lon = str(row['stop_lon'])
        #print(o_lat + ', ' + o_lon)
        #print(d_lat + ', ' + d_lon)
        # get timing info
        p = {
            "mode":"transit", 
            "transit_mode":modality,
            "origins":o_lat + ', ' + o_lon,
            "destinations":d_lat + ', ' + d_lon,
            "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
        }
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
        # determine if we're more likely to arrive @ same start time, or in next time slot
        # TODO add a catch here so we don't key error if this request fails
        #try:
        trip_length = response.json()['rows'][0]['elements'][0]['duration']['value'] / 60 # minutes
        #except:

        odds_next_time = trip_length / selected_time.duration 
        end_time = selected_time
        # given even distro. of start across operating mins within block, odds the trip ends in the same block
        if random.random() <= odds_next_time:
            # next time block
            i = times.index(selected_time)
            if (i < len(times) - 1):
                end_time = times[i+1]
            else:
                # TODO if we'd arrive outside MBTA operating hours, we need a different route/timing
                # if time = NIGHT and duration > 60 minutes
                end_time = selected_time

        self.dict = {
            # there is an option for departure time, but since we can't do times in the past
            # it gets a little wonky...
            "start_station":selected_start['stop_name'],
            "start_point":o_lat + ', ' + o_lon,
            "end_station":selected_end['stop_name'],
            "end_point":d_lat + ', ' + d_lon,
            "start_time":selected_time.text,
            "end_time":end_time.text,
            # for now, not recording the "route", but "directions" api from Google Maps could do this
            # (if it would be useful)
        }

class Genotype:
    def __init__(self):
        # TODO ramp up
        # TODO get standard distribution of quantities -- should have some
        # range and flexibility around this rough average
        # ~671000 rides on rail each day
        # ~77300 rides on bus each day
        rail_rides = []
        bus_rides = []
        for i in range(5):
            rail_rides.append(Ride('rail'))
            bus_rides.append(Ride('bus'))
        self.rail_rides = rail_rides
        self.bus_rides = bus_rides
    
    # calculates fitness of an individual
    #def fitness(self):
        # TODO
        # generate dataset of same form as existing ridership dataset based on these rides
        # count how many individuals are short/over averages
        # check how many std deviations we are from averages in data

    # returns fresh Genotype instance mutated off self
    #def mutation(self):
        # TODO

    # returns fresh Genotype instance crossing over self and other
    #def crossover(self, other):
        # TODO

    # outputs a string in json format
    def json_print(self):
        j = '{rail_rides:['
        for ride in self.rail_rides:
            j += json.dumps(ride.dict)
            j += ','
        # trailing comma
        j[-1] = ']'
        j += 'bus_rides:'
        for bus in self.bus_rides:
            j += json.dumps(bus.dict)
            j += ','
        j[-1] = ']'
        j += '}'
        return j