# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    simulation.py
#       Models impacts of changes to a rail system.
#    Spring 2024
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import genotype as g
import random
import math
import pandas as pd
from geopy import distance

rail_map = json.load(open('map.json'))
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
#model = g.from_file(model.json) # TODO
walk_speed = 0.00142 # kilometers/second

# TODO take user input
# 1. Add or remove a stop?
#   a. If adding, provide line to add to and connecting stop(s). Must be adjacent stop(s) if multiple,
#      or end-of-line if single. Also, provide co-ordinates, and validate. Behavior is likely weird for 
#      strange input coordinates far from the line.
#   b. If removing, provide a valid stop_id for the station to be removed. TODO TBD: Have the option to only
#      remove from *one* line for stations which are transfers? (e.g., make North Station green line exclusive?)

# Consider a ride starting at stop X, call the other stop Y. Assign more granular locations beyond X and Y. Select a random location (pair of coordinates) such that the location:
#   - is at most a twenty minute walk from the respective stop, and at least a five minute walk.
#   - is not nearer any other stop A than it is to X, (Note: we assume A and X both service Y (and vice-versa, for Y)).
# Call these coordinate pairs CX and CY.
def granulate_station(stop_id, tolerance = 0):
    # generate random dx/dy representing distance from center point (station). 
    # Bounded by radius 5-20 min walk (300-1200 secs), or 0.426-1.704 kilometers
    # Ensure these coordinates are closer to given stop_id than any other stop
    # Tolerance enables us to reel this in to reduce risk of infinite recursion
    distance = random.uniform(0.426, 1.704 - tolerance)
    dx = random.uniform(0, distance) * (1 if random.randint(0, 1) == 0 else -1)
    dy = math.sqrt(distance ** 2 - dx ** 2) * (1 if random.randint(0, 1) == 0 else -1)    
    # get coords of station
    latitude = 0
    longitude = 0
    for i, r in df_rail_stops.iterrows():
        if (r['stop_id'] == stop_id):
            latitude = r['stop_lat']
            longitude = r['stop_lon']
    # sanity check
    assert latitude != 0 and longitude != 0
    # calculate actual position of "granulated" station by adding relative vector to station coords
    # https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters
    new_latitude  = latitude  + (dy / distance.EARTH_RADIUS) * (180 / math.pi)
    new_longitude = longitude + (dx / distance.EARTH_RADIUS) * (180 / math.pi) / math.cos(latitude * math.pi/180)

    closest = stop_id
    closest_distance = distance.distance((latitude, longitude), (new_latitude, new_longitude))
    for i, r in df_rail_stops.iterrows():
        # calulate distance from each stop
        d = distance.distance((r['stop_lat'], r['stop_lon']), (new_latitude, new_longitude))
        if (d < closest_distance):
            closest = r['stop_id']
            closest_distance = d
            break # now we know something is faster, so we can break early (failed)

    # if not closest to the stop we started with, recurse with higher tolerance
    if stop_id != closest:
        return granulate_station(stop_id, tolerance + 0.005) # increase tolerance by 5 meters
    else:
        return new_latitude, new_longitude

# Stop Subtraction:
# 1. User selects a valid stop to remove from the MBTA. Call this stop X. Generate granular locations for all rides involving X.
# 2. All rides which include X must be re-routed. Find stop Z, which is connected to Y and is nearest to CX.
def stop_subtraction(stop_id):
    for (ride in model['rail_rides']):
        # reroute if this ride contains removed stop
        if (ride['start_id'] == stop_id or ride['end_id'] == stop_id):
            failure_point = 'start' if ride['start_id'] == stop_id else 'end'
            staying_point = 'start' if failure_point == 'end' else 'end'
            # granulate both ends
            failure_granulated = granulate_station(ride[failure_point + '_id'])
            staying_granulated = granulate_station(ride[staying_point + '_id'])
            # find a new stop Z to replace failure stop
            # consider what is nearest to failure_granulated, and what is fastest to reach staying_granulated
            # compare time to walking time to direct between granulated points (rare edge case it is next fastest route)
            z_stop_row = None
            fastest_total_time = -1
            for i, r in df_rail_stops.iterrows():
                # can't replace failed stop with itself
                if r['stop_id'] == ride[failure_point + '_id']:
                    continue
                # compute distance from failure_granulated to this stop_id
                distance = distance.distance(failure_granulated, (r['stop_lat'], r['stop_lon']))
                # calculate new walking time based on distance and assumed walk_speed
                walk_time = distance / walk_speed
                # sum walking time and time to traverse stops
                total_time = rail_map[r['stop_id']][ride[failure_point + '_id']] + walk_time
                # pick best time to continue with
                if (fastest_total_time == -1 or total_time < fastest_total_time):
                    fastest_total_time = total_time
                    z_stop_row = r
            # replace failed stop with z_stop_row's info
            ride[failure_point + '_id'] = z_stop_row['stop_id']
            ride[failure_point + '_point'] = str(z_stop_row['stop_lat']) + ', ' + str(z_stop_row['stop_lon'])
            ride[failure_point + '_station'] = z_stop_row['stop_name']

# Stop Addition:
# 1. User inputs coordinates and a valid line(s) to add the stop to. Call this stop N. 
# 2. Find the nearest stops to N (which N may poach riders from). Call these stops Pi such that for all Pi:
#   A. N is less than a 40 minute walk away. Ergo, N is a reasonable walking distance from the ride’s granular location.
# 3. For all Pi find all rides that include at least one Pi. Generate granular locations for them. 
# 4. Then, from this set of rides, find all poachable riders, Ri  such that for each:
#   A. The other end of their route, O, is serviceable by N 
#   B. Using N is more efficient
#       i. Calculate walk time to N and walk time to Pi
#       ii. Calculate transit time for both. 
#           a. If N is between two existing stops:
#
#               1 -- N -- 2 -- O
#	
#               - Calculate the transit ride time from 1 to O (or vice versa depending on ride)
#               - Calculate the transit ride time from 2 to O (or vice versa)
#               - Compute the difference. Add to the transit ride time from 2 to O a fraction of the difference based on how close N is to 2 vs. 1.
#           b. If N is expanding a line:
#
#               N -- 2 -- O
#
#               - Calculate the transit ride time from 2 to O (or vice versa)
#               - Add based on the distance from N to 2
#               Note: For both of these, depending on line, will need to look at how long the 
#                     subway generally takes to travel such distance. This can probably be a 
#                     precalculated constant for each line just as a MPH or something.
#       iii. Sum walk and transit time. Walk time should be weighted somewhat to favor less walking in the overall route.
# 5. For all Ri, replace Pi with N.
#
# At this point, ridership metrics can be recalculated. 
# For now, we assume no impact of a new stop on the rest of the route, e.g.:
#
#     1 -- 2 -------- O     ->     1 -- 2 -       - O
#                                           \   /
#                                            | |
#                                             N
# Is not a concern.
def stop_addition(coords, line, neighbor_1, neighbor_2='place-xxxxx'):
