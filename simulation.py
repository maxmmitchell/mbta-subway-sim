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
import json
import pandas as pd
import click
import os
from geopy import distance

OUT_DIR = f"{os.getcwd()}/sim_out/"
IN_DIR = f"{os.getcwd()}/sim_in_default/"

df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')

rail_map = json.load(open(f'{IN_DIR}map.json'))
dict_dict = {
    "blue":json.load(open(f'{IN_DIR}blue.json'))['stops'],
    "red-a":json.load(open(f'{IN_DIR}red-a.json'))['stops'],
    "red-b":json.load(open(f'{IN_DIR}red-b.json'))['stops'],
    "orange":json.load(open(f'{IN_DIR}orange.json'))['stops'],
    "green-e":json.load(open(f'{IN_DIR}green-e.json'))['stops'],
    "green-d":json.load(open(f'{IN_DIR}green-d.json'))['stops'],
    "green-c":json.load(open(f'{IN_DIR}green-c.json'))['stops'],
    "green-b":json.load(open(f'{IN_DIR}green-b.json'))['stops']
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

model = g.Genotype(False)
model.from_file("60_model_map.json") # TODO switch to full size model

# NOTE: DO NOT CHANGE THIS! SOME THINGS IN THIS FILE HAVE BEEN MANUALLY CALCULATED
# WITH THIS VALUE WHICH I KNOW IS BAD AND SHOULD BE FIXED; THEY'RE DOCUMENTED AND I
# HOPE I GET TO IT BUT FUTURE MAX DON'T CHANGE THIS PLEASE I BEG OF YOU
walk_speed = 0.00142 # kilometers/second

# Consider a ride starting at stop X, call the other stop Y. Assign more granular locations beyond X and Y. Select a random location (pair of coordinates) such that the location:
#   - is at most a twenty minute walk from the respective stop, and at least a five minute walk.
#   - is not nearer any other stop A than it is to X, (Note: we assume A and X both service Y (and vice-versa, for Y)).
# Call these coordinate pairs CX and CY.
def granulate_station(stop_id, tolerance = 0):
    # generate random dx/dy representing distance from center point (station). 
    # Bounded by radius 5-20 min walk (300-1200 secs), or 0.426-1.704 kilometers
    # Ensure these coordinates are closer to given stop_id than any other stop
    # Tolerance enables us to reel this in to reduce risk of infinite recursion
    dist = random.uniform(0.426, 1.704 - tolerance)
    dx = random.uniform(0, dist) * (1 if random.randint(0, 1) == 0 else -1)
    dy = math.sqrt(dist ** 2 - dx ** 2) * (1 if random.randint(0, 1) == 0 else -1)    
    # get coords of station
    latitude = 0
    longitude = 0
    for i, r in df_rail_stops.iterrows():
        if r['stop_id'] == stop_id:
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
        if d < closest_distance:
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
def recalculate_map():
    dict_graph = {}
    def trip_length(line, origin, line_stops, stop, sofar, dir, curr_line, visited_lines):
        if stop == 'place-xxxxx':
            return
        neighbor = 'inbound_neighbor' if dir == 'i' else 'outbound_neighbor'
        time = 'inbound_time' if dir == 'i' else 'outbound_time'
        try:
            dict_graph[origin][stop] = sofar
        except KeyError:
            dict_graph[origin] = {}
            dict_graph[origin][stop] = sofar
        trip_length(line, origin, line_stops, line_stops[stop][neighbor], sofar + float(line_stops[stop][time]), dir, curr_line, visited_lines)
        pot_trans = line_stops[stop]['transfer']
        if pot_trans != 'none' and not pot_trans in visited_lines:
            visited_lines.append(pot_trans)
            trip_length(line, origin, dict_dict[pot_trans], stop, sofar, 'i', pot_trans, visited_lines)
            trip_length(line, origin, dict_dict[pot_trans], stop, sofar, 'o', pot_trans, visited_lines)

    for line, line_stops in dict_dict.items():
        for stop in line_stops:
            trip_length(line, stop, line_stops, stop, 0, 'i', line, [line])
            trip_length(line, stop, line_stops, stop, 0, 'o', line, [line])
    
    return dict_graph

# Stop Subtraction:
# 1. User selects a valid stop to remove from the MBTA. Call this stop X. Generate granular locations for all rides involving X.
# 2. All rides which include X must be re-routed. Find stop Z, which is connected to Y and is nearest to CX.
# Note: this mutates the model we've imported (intentionally). An original version still exists on file.
def stop_subtraction(stop_id):
    global rail_map
    log = {}
    for ride in model.rail_rides:
        # reroute if this ride contains removed stop
        if ride.dict['start_id'] == stop_id or ride.dict['end_id'] == stop_id:
            failure_point = 'start' if ride.dict['start_id'] == stop_id else 'end'
            staying_point = 'start' if failure_point == 'end' else 'end'
            # granulate both ends
            failure_granulated = granulate_station(ride.dict[failure_point + '_id'])
            staying_granulated = granulate_station(ride.dict[staying_point + '_id'])
            # find a new stop Z to replace failure stop
            # consider what is nearest to failure_granulated, and what is fastest to reach staying_granulated
            # compare time to walking time to direct between granulated points (rare edge case it is next fastest route)
            z_stop_row = None
            fastest_total_time = -1
            original_total_time = -1
            for i, r in df_rail_stops.iterrows():
                # compute distance from failure_granulated to this stop_id
                dist = distance.distance(failure_granulated, (r['stop_lat'], r['stop_lon'])).km
                # calculate new walking time based on distance and assumed walk_speed
                walk_time = dist / walk_speed / 60
                # sum walking time and time to traverse stops
                total_time = 0
                try:
                    total_time = rail_map[r['stop_id']][ride.dict[failure_point + '_id']] + float(walk_time)
                except KeyError:
                    continue
                # can't replace failed stop with itself
                if r['stop_id'] == ride.dict[failure_point + '_id']:
                    original_total_time = total_time
                    continue
                # pick best time to continue with
                if fastest_total_time == -1 or total_time < fastest_total_time:
                    fastest_total_time = total_time
                    z_stop_row = r
            # replace failed stop with z_stop_row's info
            ride.dict[failure_point + '_id'] = z_stop_row['stop_id']
            ride.dict[failure_point + '_point'] = str(z_stop_row['stop_lat']) + ', ' + str(z_stop_row['stop_lon'])
            ride.dict[failure_point + '_station'] = z_stop_row['stop_name']
            # log stop selected for replacement and change in travel time
            delta_time = fastest_total_time - original_total_time
            try:
                log[z_stop_row['stop_id']].append(delta_time)
            except KeyError:
                log[z_stop_row['stop_id']] = [delta_time]

    # Modify maps
    for line_dict in dict_dict.values():
        if not stop_id in line_dict.keys():
            continue

        inbound_neighbor = line_dict[stop_id]["inbound_neighbor"]
        outbound_neighbor = line_dict[stop_id]["outbound_neighbor"]
        if inbound_neighbor != "place-xxxxx":
            line_dict[inbound_neighbor]["outbound_neighbor"] = outbound_neighbor
            line_dict[inbound_neighbor]["outbound_time"] = float(line_dict[inbound_neighbor]["outbound_time"]) + float(line_dict[stop_id]["outbound_time"])
        if outbound_neighbor != "place-xxxxx":
            line_dict[outbound_neighbor]["inbound_neighbor"] = inbound_neighbor
            line_dict[outbound_neighbor]["inbound_time"] = float(line_dict[outbound_neighbor]["inbound_time"]) + float(line_dict[stop_id]["inbound_time"])
        del line_dict[stop_id] 
    rail_map = recalculate_map()
    return log

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
    global rail_map
    # TODO based on neighbors we could deduce line, but for right now, 
    # assume user has knowledge of our mapping system and knows where their new stop belongs
    dict_line = dict_dict[line]
    speed_line = dict_speed[line]
    log = {}

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
    time_to_1 = (distance.distance(coords, neighbor_1_coords).km / speed_line) / 60 # convert to minutes from seconds
    time_to_2 = (distance.distance(coords, neighbor_2_coords).km / speed_line) / 60 if neighbor_2 != 'place-xxxxx' else -1 # end of line times should keep with the standard set

    # insert new stop (N) into line on mapping
    outbound_from_1 = dict_line[neighbor_1]['outbound_neighbor'] == neighbor_2
    dict_line['place-usern'] = {}
    dict_line['place-usern']['outbound_neighbor'] = neighbor_2 if outbound_from_1 else neighbor_1
    dict_line['place-usern']['outbound_time'] = time_to_2 if outbound_from_1 else time_to_1
    dict_line['place-usern']['inbound_neighbor'] = neighbor_1 if outbound_from_1 else neighbor_2
    dict_line['place-usern']['inbound_time'] = time_to_1 if outbound_from_1 else time_to_2
    dict_line['place-usern']['transfer'] = 'none'

    # modify neighbors
    dict_line[neighbor_1]['outbound_neighbor' if outbound_from_1 else 'inbound_neighbor'] = 'place-usern'
    dict_line[neighbor_1]['outbound_time' if outbound_from_1 else 'inbound_time'] = time_to_1
    if neighbor_2 != 'place-xxxxx':
        dict_line[neighbor_2]['inbound_neighbor' if outbound_from_1 else 'outbound_neighbor'] = 'place-usern'
        dict_line[neighbor_2]['inbound_time' if outbound_from_1 else 'outbound_time'] = time_to_2

    # recalculate EVERYTHING distance-wise
    rail_map = recalculate_map()
    print(json.dumps(rail_map, indent=4))

    # find poachable stops 
    poachable_stops = {}
    # N is less than a 40 minute walk -- 2400 seconds -> 3.408 km
    # Ergo, N is in theory a reasonable walking distance from the ride’s granular location.
    for i, r in df_rail_stops.iterrows():
        dist = distance.distance(coords, (r['stop_lat'], r['stop_lon']))
        if dist < 3.408:
            poachable_stops[r['stop_id']] = dist
        
    # for each ride including a poachable stop: 
    for ride in model.rail_rides:
        if ride.dict['start_id'] in poachable_stops.keys() or ride.dict['end_id'] in poachable_stops.keys():
            # If both start and end are poachable, poach the one closer to N
            poach_point = 'start' if ride.dict['start_id'] in poachable_stops.keys() else 'end'
            destination_point = 'end' if poach_point == 'start' else 'start'
            if ride.dict['start_id'] in poachable_stops.keys() and ride.dict['end_id'] in poachable_stops.keys():
                poach_point = 'start' if poachable_stops[ride.dict['start_id']] < poachable_stops[ride.dict['end_id']] else 'end'
                destination_point_point = 'end' if poach_point == 'start' else 'start'

            poach_granulated = granulate_station(ride.dict[poach_point + '_id'])
            # determine if N is more efficient 
            walk_time_N = distance.distance(coords, poach_granulated).km / walk_speed / 60 # convert seconds to minutes
            walk_time_poach = distance.distance(ride.dict[poach_point + '_point'], poach_granulated).km / walk_speed / 60 
            rail_time_N = rail_map['place-usern'][ride.dict[destination_point + '_id']]
            rail_time_poach = rail_map[ride.dict[poach_point + '_id']][ride.dict[destination_point + '_id']]
            if walk_time_N + rail_time_N < walk_time_poach + rail_time_poach:
                delta_time = (walk_time_N + rail_time_N) - (walk_time_poach + rail_time_poach)
                try:
                    log[ride.dict[poach_point + '_id']].append(delta_time)
                except KeyError:
                    log[ride.dict[poach_point + '_id']] = [delta_time]
                # N is more efficient, replace poach_point
                ride.dict[poach_point + '_id'] = 'place-usern'
                ride.dict[poach_point + '_point'] = str(coords)
                ride.dict[poach_point + '_station'] = 'User Stop N'
    return log

@click.command()
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Run the simulation in interactive mode."
) # TODO implement interactive mode
@click.option(
    "--add/--subtract",
    "-a/-s",
    required=True,
    help="Elect to add or remove a station."
)
@click.option(
    "--station",
    multiple=True,
    required=True,
    help="Station(s) for either addition or subtraction, by their `stop_id`. In subtraction mode, this station is removed. In addition, these station(s) indicate which station(s) to add the new station between. If only one station is provided in addition mode, it is assumed that the new station is to be added at the end of the line."
)
@click.option(
    "--latitude",
    type=float,
    help="Latitude to place new station at."
)
@click.option(
    "--longitude",
    type=float,
    help="Longitude to place new station at."
)
@click.option(
    "--line",
    help="Line to place new stop on. Valid options are: red-a, red-b, blue, orange, green-b, green-c, green-d, and green-e."
)
@click.option(
    "--from-file",
    default="",
    help="Set a different directory from which to pull the input model, and map files. Paths are assumed local to current working directory."
)
@click.option(
    "--output",
    default="",
    help="Set a different directory in which to deposit the output log files. Paths are assumed local to current working directory."
)
# Gather user input on CLI and validate
def cli(interactive, add, station, latitude, longitude, line, from_file, output):
    if output != "":
        validate_directory(output)
        global OUT_DIR
        OUT_DIR = os.getcwd() + output

    if from_file != "":
        validate_directory(from_file)
        global IN_DIR 
        IN_DIR = os.getcwd() + from_file

        global df_rail_stops
        global rail_map
        global dict_dict

        df_rail_stops = pd.read_csv(f'{IN_DIR}MBTA_Rail_Stops.csv')
        rail_map = json.load(open(f'{IN_DIR}map.json'))
        dict_dict = {
            "blue":json.load(open(f'{IN_DIR}blue.json'))['stops'],
            "red-a":json.load(open(f'{IN_DIR}red-a.json'))['stops'],
            "red-b":json.load(open(f'{IN_DIR}red-b.json'))['stops'],
            "orange":json.load(open(f'{IN_DIR}orange.json'))['stops'],
            "green-e":json.load(open(f'{IN_DIR}green-e.json'))['stops'],
            "green-d":json.load(open(f'{IN_DIR}green-d.json'))['stops'],
            "green-c":json.load(open(f'{IN_DIR}green-c.json'))['stops'],
            "green-b":json.load(open(f'{IN_DIR}green-b.json'))['stops']
        }

    if interactive:
        raise click.BadParameter(f"Interactive mode unimplemented :(")
    else:
        log = {}
        if add:
            validate_addition([latitude, longitude], line, station[0], station[1] if len(station) == 2 else 'place-xxxxx')
            log = stop_addition([latitude, longitude], line, station[0], station[1] if len(station) == 2 else 'place-xxxxx')
        else:
            validate_subtraction(station[0])
            log = stop_subtraction(station[0])
        serialize(log)

#   TODO: Specify available transfers?
#   Behavior is likely weird for strange input coordinates far from the line, but that is on user.
#   TODO add notes to README to guide user on lines, stop_ids, etc.
def validate_addition(coords, line, neighbor_1, neighbor_2='place-xxxxx'):
    # coords must be on earth
    if not (coords[0] > -180 and coords[0] < 180 and coords[1] > -90 and coords[1] < 90):
        raise click.BadParameter(f"Provided coordinates \"{str(coords)}\" for placement of new station are not valid.")
    # line must be valid
    if not line in dict_dict.keys():
        raise click.BadParameter(f"Provided line \"{line}\" is not a valid line. Valid options are: red-a, red-b, blue, orange, green-b, green-c, green-d, and green-e. For more details on these lines, please consult README.md.")
    # neighbors must be neighbors for new stop to go in between them
    if dict_dict[line][neighbor_1]["inbound_neighbor"] != neighbor_2 and dict_dict[line][neighbor_1]["outbound_neighbor"] != neighbor_2:
        raise click.BadParameter(f"Provided stations \"{neighbor_1}\" and \"{neighbor_2}\" are invalid for stop addition. Provided stations must neighbor each other on the provided line, \"{line}\". For more details on these lines, please consult README.md.")

#   TODO TBD: Have the option to only remove from *one* line for stations which are transfers? 
#   (e.g., make North Station green line exclusive?)
def validate_subtraction(stop_id):
    # Check that stop_id is valid
    for i, r in df_rail_stops.iterrows():
        if r['stop_id'] == stop_id:
            return
    raise click.BadParameter(f"Provided stop_id \"{stop_id}\" is not a valid stop. Please consult your MBTA_Rail_Stops.csv file for valid stop_id values and check your spelling.")

def validate_directory(path):
    if not (os.path.exists(os.getcwd() + path) and os.path.isdir(os.getcwd() + path)):
        raise click.BadParameter(f"Provided directory \"{path}\" is invalid. Make sure it exists and is a directory!")

def serialize(log):
    with open(f"{OUT_DIR}sim_model.json", 'w') as f:
        f.write(model.json_print())
    with open(f"{OUT_DIR}sim_log.json", 'w') as f:
        f.write(json.dumps(log, indent=4))
    with open(f"{OUT_DIR}sim_map.json", 'w') as f:
        f.write(json.dumps(rail_map, indent=4))
    for line, line_dict in dict_dict.items():
        with open(f"{OUT_DIR}{line}.json", 'w') as f:
            f.write(json.dumps(line_dict, indent=4))

if __name__ == "__main__":
    # TODO remove these dummy values and take/validate user input
    # remove = "place-davis"
    # add_coords = (42.380869, -71.119685)
    # add_neighbor_1 = "place-portr"
    # add_neighbor_2 = "place-harsq"
    cli()

