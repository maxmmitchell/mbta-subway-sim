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
import statistics as stats
import sys

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
rail_ons_stdev = stats.stdev(df_rail_ridership['average_ons'].tolist())
rail_offs_stdev = stats.stdev(df_rail_ridership['average_offs'].tolist())
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
df_bus_ridership = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')
bus_ons_stdev = stats.stdev(df_bus_ridership['average_ons'].tolist())
bus_offs_stdev = stats.stdev(df_bus_ridership['average_offs'].tolist())
df_bus_stops = pd.read_csv('stops-20190808-modified.csv')

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
    # modality of none implies an empty ride
    def __init__(self, modality='none'):
        self.dict = {}
        if modality == 'none':
            return
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
        # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
        # is associated with a direction (0 or 1), and that should be used to limit the possible
        # end stations, for further accuracy/consistency with the data! Do we need each station to
        # know all possible reachable stations given its current direction? an option, which could hasten
        # the station selection process and give us what we want here...
        selected_end = self.pick_station(selected_time.text, modality, 'off')
        # ensure end is different from start
        while str(selected_end['stop_id']) == str(selected_start['stop_id']):
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
        try:
            trip_length = response.json()['rows'][0]['elements'][0]['duration']['value'] / 60 # minutes
        except:
            print('Failed querying:', file=sys.stderr)
            print(json.dumps(p, indent=4), file=sys.stderr)
            print('Partial response:', file=sys.stderr)
            print(json.dumps(response.json(), indent=4), file=sys.stderr)
            self.dict = Ride(modality).dict
            return

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
            "start_id":selected_start['stop_id'],
            "direction":selected_start['direction_id'],
            "end_station":selected_end['stop_name'],
            "end_point":d_lat + ', ' + d_lon,
            "end_id":selected_end['stop_id'],
            "start_time":selected_time.text,
            "end_time":end_time.text,
            # for now, not recording the "route", but "directions" api from Google Maps could do this
            # (if it would be useful)
        }

class GenoStats:
    def __init__(self):
        self.dict = {}

    def add_ride(self, stop_id, stop_time, direction, is_on):
        if stop_id not in self.dict:
            self.dict[stop_id] = {}
            for time in times:
                self.dict[stop_id][time.text] = [[0, 0], [0, 0]] # at this stop at this time, 0 ons and 0 offs
        # add ride
        self.dict[stop_id][stop_time][direction][0 if is_on else 1] += 1

    def get_stats(self, stop_id, stop_time, direction, is_on):
        return self.dict[stop_id][stop_time][direction][0 if is_on else 1]

class Genotype:
    def __init__(self, random=True):
        # TODO get standard distribution of quantities -- should have some
        # range and flexibility around this rough average -- this will require changing
        # crossover function! (or get bounds error)
        # ~671000 rides on rail each day
        # ~77300 rides on bus each day
        if random:
            rail_rides = []
            bus_rides = []
            self.rail_stats = GenoStats()
            self.bus_stats = GenoStats()
            for i in range(671000):
                rail_rides.append(Ride('rail'))
                self.rail_stats.add_ride(rail_rides[-1].dict['start_id'], rail_rides[-1].dict['start_time'], rail_rides[-1].dict['direction'], True) 
                self.rail_stats.add_ride(rail_rides[-1].dict['end_id'], rail_rides[-1].dict['end_time'], rail_rides[-1].dict['direction'], False) 
                if i < 77300:
                    bus_rides.append(Ride('bus'))
                    self.bus_stats.add_ride(bus_rides[-1].dict['start_id'], bus_rides[-1].dict['start_time'], bus_rides[-1].dict['direction'], True) 
                    self.bus_stats.add_ride(bus_rides[-1].dict['end_id'], bus_rides[-1].dict['end_time'], bus_rides[-1].dict['direction'], False) 
            self.rail_rides = rail_rides
            self.bus_rides = bus_rides
        else:
            self.rail_rides = []
            self.bus_rides = []
            self.rail_stats = GenoStats()
            self.bus_stats = GenoStats()
    
    # other ways to initialize a Genotype
    def from_file(self, fname):
        with open(fname, 'r') as f:
            j = json.load(f)
            for ride in j['rail_rides']:
                r = Ride()
                r.dict = ride
                self.rail_rides.append(r)
                self.rail_stats.add_ride(ride['start_id'], ride['start_time'], ride['direction'], True) 
                self.rail_stats.add_ride(ride['end_id'], ride['end_time'], ride['direction'], False) 
            for ride in j['bus_rides']:
                r = Ride()
                r.dict = ride
                self.bus_rides.append(r)
                self.bus_stats.add_ride(ride['start_id'], ride['start_time'], ride['direction'], True) 
                self.bus_stats.add_ride(ride['end_id'], ride['end_time'], ride['direction'], False) 
            f.close()

    def fitness_rideset(self, modality):
        df = df_rail_ridership if modality == 'rail' else df_bus_ridership
        stats = self.rail_stats if modality == 'rail' else self.bus_stats
        stdev_on = rail_ons_stdev if modality == 'rail' else bus_ons_stdev
        stdev_off = rail_offs_stdev if modality == 'rail' else bus_offs_stdev

        difference = 0 
        deviation = 0
        for index, row in df.iterrows():
            # check difference between known stats and our stats
            known_ons = row['average_ons']
            known_offs = row['average_offs']
            our_ons = 0
            our_offs = 0
            if row['stop_id'] in stats.dict:
                our_ons = stats.dict[row['stop_id']][row['time_period_name']][int(row['direction_id'])][0]
                our_offs = stats.dict[row['stop_id']][row['time_period_name']][int(row['direction_id'])][1] 
            # normal distribution has 68.4% at 1 std deviation below/above
            difference += abs(known_ons - our_ons) + abs(known_offs - our_offs)
            # mean = 𝜇
            # stdev = 𝜎
            # data point = 𝑥
            # x is |𝑥−𝜇|/𝜎 std deviations from mean
            deviation += (abs(our_ons - known_ons) / stdev_on) + (abs(our_offs - known_offs) / stdev_off)
        return difference, deviation

    # calculates fitness of an individual
    def fitness(self):
        # TODO
        # count how many rides are short/over averages
        # check how many std deviations we are from averages in data
        return self.fitness_rideset('rail')[1] + self.fitness_rideset('bus')[1]

    # returns fresh Genotype instance mutated off self
    def mutation(self):
        # randomly modify rides
        # TODO tweak odds accordingly as use continues
        # right now just randomly generates a new ride, but could also consider more granular randomness,
        # as this still uses whatever odds exist in our original ride generation process
        new_genotype = Genotype()
        new_genotype.rail_rides = [rr if random.random() < 0.5 else Ride('rail') for rr in self.rail_rides]
        new_genotype.bus_rides = [br if random.random() < 0.5 else Ride('bus') for br in self.bus_rides]
        return new_genotype

    # returns fresh Genotype instance crossing over self and other
    def crossover(self, other):
        new_genotype = Genotype()
        # TODO: if we ever have variable ride counts, this will need fixing or we'll get a bounds error
        new_genotype.rail_rides = [self.rail_rides[i] if random.random() < 0.5 else other.rail_rides[i] for i in range(len(self.rail_rides))]
        new_genotype.bus_rides = [self.bus_rides[i] if random.random() < 0.5 else other.bus_rides[i] for i in range(len(self.bus_rides))]
        return new_genotype

    # outputs a string in json format
    def json_print(self, indentation=4):
        j = '{\n"rail_rides": ['
        for ride in self.rail_rides:
            j += json.dumps(ride.dict, indent=indentation)
            j += '],' if ride is self.rail_rides[-1] else ','
        j += '\n"bus_rides": ['
        for bus in self.bus_rides:
            j += json.dumps(bus.dict, indent=indentation)
            j += ']' if bus is self.bus_rides[-1] else ','
        j += '}'
        return j