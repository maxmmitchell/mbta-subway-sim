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

df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')

rail_map = json.load(open('map.json'))
dict_blue = json.load(open('blueline.json'))['stops']
dict_red_a = json.load(open('redline-a.json'))['stops']
dict_red_b = json.load(open('redline-b.json'))['stops']
dict_orange = json.load(open('orangeline.json'))['stops']
dict_green_e = json.load(open('greenline-e.json'))['stops']
dict_green_d = json.load(open('greenline-d.json'))['stops']
dict_green_c = json.load(open('greenline-c.json'))['stops']
dict_green_b = json.load(open('greenline-b.json'))['stops']
dict_dict = {
    "blue":dict_blue,
    "red-a":dict_red_a,
    "red-b":dict_red_b,
    "orange":dict_orange,
    "green-e":dict_green_e,
    "green-d":dict_green_d,
    "green-c":dict_green_c,
    "green-b":dict_green_b
}
dict_speed = { # served in kilometers/second (for consistent units), based on historical averages
    "blue":0.007465568,
    "red-a":0.005990336,
    "red-b":0.005990336,
    "orange":0.00648208,
    "green-e":0.004649216, # I mean, I know it's slow, but goodness gravy
    "green-d":0.004649216, # seeing it as a number really helps you appreciate
    "green-c":0.004649216, # just how abysmally slow the grean line truly is,
    "green-b":0.004649216  # even when compared to the other "slow" lines...
}

#model = g.from_file(model.json) # TODO

# NOTE: DO NOT CHANGE THIS! SOME THINGS IN THIS FILE HAVE BEEN MANUALLY CALCULATED
# WITH THIS VALUE WHICH I KNOW IS BAD AND SHOULD BE FIXED; THEY'RE DOCUMENTED AND I
# HOPE I GET TO IT BUT FUTURE MAX DON'T CHANGE THIS PLEASE I BEG OF YOU
walk_speed = 0.00142 # kilometers/second

# TODO take user input -- use click for this?
# 1. Add or remove a stop?
#   a. If adding, provide line to add to and connecting stop(s). Must be adjacent stop(s) if multiple,
#      or end-of-line if single. Also, provide co-ordinates, and validate. Behavior is likely weird for 
#      strange input coordinates far from the line.
#      TODO: Specify available transfers?
#   b. If removing, provide a valid stop_id for the station to be removed. TODO TBD: Have the option to only
#      remove from *one* line for stations which are transfers? (e.g., make North Station green line exclusive?)

# TODO TODO TODO both of these overarching functions should compute some stats as they modify:
# Which stops are being rerouted? Who's being poached? If ride times are changing, who's affected? Do things get faster or
# slower and for whom?

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

# assumes local variables of the various maps have been modified
# returns new value for distance matrix
# TODO the line index is probably gonna fuck this all up
# Note: I'm not sure why I wrote the above comment. I think this works but I'm ready
#       to be wrong.
def recalculate_map():
    dict_graph = {}

    def distance(line, origin, line_stops, stop, sofar, dir, curr_line, visited_lines):
        if stop == 'place-xxxxx':
            return
        neighbor = 'inbound_neighbor' if dir == 'i' else 'outbound_neighbor'
        time = 'inbound_time' if dir == 'i' else 'outbound_time'
        dict_graph[origin][stop] = sofar
        distance(line, origin, line_stops, line_stops[stop][neighbor], sofar + float(line_stops[stop][time]), dir, curr_line, visited_lines)
        pot_trans = line_stops[stop]['transfer']
        if pot_trans != 'none' and not pot_trans in visited_lines:
            visited_lines.append(pot_trans)
            distance(line, origin, dict_dict[pot_trans], stop, sofar, 'i', pot_trans, visited_lines)
            distance(line, origin, dict_dict[pot_trans], stop, sofar, 'o', pot_trans, visited_lines)

    for line, line_stops in dict_dict:
        for stop in line_stops["stops"]:
            distance(line, stop, line_stops, stop, 0, 'i', line, [line])
            distance(line, stop, line_stops, stop, 0, 'o', line, [line])
    
    return dict_graph

# Stop Subtraction:
# 1. User selects a valid stop to remove from the MBTA. Call this stop X. Generate granular locations for all rides involving X.
# 2. All rides which include X must be re-routed. Find stop Z, which is connected to Y and is nearest to CX.
# Note: this mutates the model we've imported (intentionally). An original version still exists on file.
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
    # Modify maps
    for line_dict in dict_dict:
        try:
            inbound_neighbor = line_dict["stops"][stop_id]["inbound_neighbor"]
            outbound_neighbor = line_dict["stops"][stop_id]["outbound_neighbor"]
            if inbound_neighbor != "place-xxxxx":
                line_dict["stops"][inbound_neighbor]["outbound_neighbor"] = outbound_neighbor
            if outbound_neighbor != "place-xxxxx"
                line_dict["stops"][outbound_neighbor]["inbound_neighbor"] = inbound_neighbor
            del line_dict["stops"][stop_id] 
        except KeyError:
            continue
    new_rail_map = recalculate_map()

# Stop Addition:
# 1. User inputs coordinates and a valid line(s) to add the stop to. Call this stop N. 
# 2. Find the nearest stops to N (which N may poach riders from). Call these stops Pi such that for all Pi:
#   A. N is less than a 40 minute walk away. Ergo, N is a reasonable walking distance from the ride’s granular location.
# 3. For all Pi find all rides that include at least one Pi. Generate granular locations for them. 
# 4. Then, from this set of rides, find all poachable riders, Ri  such that for each:
#   A. Using N is more efficient
#       i. Calculate walk time to N and walk time to Pi
#       ii. Calculate transit time for both. Use historical averages of line speeds and distance to neighbors to estimate
#           how N will integrate to the map, and recalulate the map.
#       iii. Sum walk and transit time. Walk time should be weighted somewhat to favor less walking in the overall route.
# 5. For all Ri, replace Pi with N.
#
# At this point, ridership metrics can be recalculated. 
def stop_addition(coords, line, neighbor_1, neighbor_2='place-xxxxx'):
    # TODO based on neighbors we could deduce line, but for right now, 
    # assume user has knowledge of our mapping system and knows where their new stop belongs
    dict_line = dict_dict[line]
    speed_line = dict_speed[line]

    # find coordinates for neighbors
    neighbor_1_coords = (0,0)
    neighbor_2_coords = (0,0)
    for i, r in df_rail_stops.iterrows():
        if r['stop_id'] == neighbor_1:
            neighbor_1_coords = (r['stop_lat'], r['stop_lon'])
        if r['stop_id'] == neighbor_2:
            neighbor_2_coords = (r['stop_lat'], r['stop_lon'])

    # determine transit times for new stop to/from its neighbors
    # assume straight line travel underground, nevermind the fact that this would require
    # crazy expensive overhauls to the existing tunnels -- that stuff is 'boring' ;)
    # this is a decent way to estimate; it's not exactly the same as how we calulated for the extant
    # stops, but I've compared a few anecdotally and it seems ok for our purposes right now.
    time_to_1 = (distance.distance(coords, neighbor_1_coords) / speed_line) / 60 # convert to minutes from seconds
    time_to_2 = (distance.distance(coords, neighbor_2_coords) / speed_line) / 60 if neighbor_2 != 'place-xxxxx' else -1 # end of line times should keep with the standard set

    # insert new stop (N) into line on mapping
    outbound_from_1 = neighbor_1['outbound_neighbor'] == neighbor_2
    dict_line['place-usern']['outbound_neighbor'] = neighbor_1 if outbound_from_1 else neighbor_2
    dict_line['place-usern']['outbound_time'] = time_to_1 if outbound_from_1 else time_to_2
    dict_line['place-usern']['inbound_neighbor'] = neighbor_2 if outbound_from_1 else neighbor_1
    dict_line['place-usern']['inbound_time'] = time_to_2 if outbound_from_1 else time_to_1
    dict_line['place-usern']['transfer'] = 'none'

    # modify neighbors
    dict_line[neighbor_1]['outbound_neighbor' if outbound_from_1 else 'inbound_neighbor'] = 'place-usern'
    dict_line[neighbor_1]['outbound_time' if outbound_from_1 else 'inbound_time'] = time_to_1
    if (neighbor_2 != 'place-xxxxx'):
        dict_line[neighbor_2]['inbound_neighbor' if outbound_from_1 else 'outbound_neighbor'] = 'place-usern'
        dict_line[neighbor_2]['inbound_time' if outbound_from_1 else 'outbound_time'] = time_to_2

    # recalculate EVERYTHING distance-wise
    new_rail_map = recalculate_map()

    # find poachable stops 
    poachable_stops = []
    # N is less than a 40 minute walk -- 2400 seconds -> 3.408 km
    # Ergo, N is in theory a reasonable walking distance from the ride’s granular location.
    for i, r in df_rail_stops.iterrows():
        distance = distance.distance(coords, (r['stop_lat'], r['stop_lon']))
        if distance < 3.408:
            poachable_stops.append(r['stop_id'])
        
    # for each ride including a poachable stop: 
    for (ride in model['rail_rides']):
        # TODO: What does it mean if both the start and finish are "poachable?"
        # You shouldn't poach both, but how do we decide which to poach?
        if (ride['start_id'] in poachable_stops or ride['end_id'] in poachable_stops):
            poach_point = 'start' if ride['start_id'] in poachable_stops else 'end'
            destination_point = 'end' if ride['start_id'] in poachable_stops else 'start'
            poach_granulated = granulate_station(ride[poach_point + '_id'])
            # determine if N is more efficient 
            walk_time_N = distance.distance(coords, poach_granulated) / walk_speed / 60 # convert seconds to minutes
            walk_time_poach = distance.distance(ride[poach_point + '_coords'], poach_granulated) / walk_speed / 60 
            rail_time_N = new_rail_map['place-usern'][ride[destination_point + '_id']]
            rail_time_poach = new_rail_map[ride[poach_point + '_id']][ride[destination_point + '_id']]
            if walk_time_N + rail_time_N < walk_time_poach + rail_time_poach:
                # N is more efficient, replace poach_point
                ride[poach_point + '_id'] = 'place-usern'
                ride[poach_point + '_point'] = str(coords)
                ride[poach_point + '_station'] = 'User Stop N'

if __name__ == "__main__":
    # TODO remove these dummy values and take/validate user input
    remove = "place-davis"
    add_coords = (42.380869, -71.119685)
    add_neighbor_1 = "place-portr"
    add_neighbor_2 = "place-harvd"

