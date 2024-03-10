# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    data.py
#        Quick and dirty way to mess with CSV data
#    Fall 2023
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import csv
import pandas as pd
import requests
import json
import math

df_rail = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_bus = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
df_bus_stops = pd.read_csv('MBTA_Bus_Stops.csv')
df_stops = pd.read_csv('stops-20190808-modified.csv')
df_rail_all = pd.read_csv('MBTA_Rail_Ridership_All.csv')

# # # # # # # # # # # # # # #
# Calculating Std. Deviation
# For All Stops At All Times
# # # # # # # # # # # # # # #

list_std_dev_ons = []
list_mean_ons = []
list_std_dev_offs = []
list_mean_offs = []

for index, rrow in df_rail.iterrows():
    sum_ons = 0
    num_vals_ons = 0
    vals_ons = []
    sum_offs = 0
    num_vals_offs = 0
    vals_offs = []
    # 1. Find the mean across the years
    for andex, arow in df_rail_all.iterrows():
        if (arow['stop_id'] == rrow['stop_id'] and arow['direction_id'] == rrow['direction_id'] and arow['time_period_name'] == rrow['time_period_name']):
            sum_ons += arow['average_ons']
            num_vals_ons += 1
            vals_ons.append(arow['average_ons'])
            sum_offs += arow['average_offs']
            num_vals_offs += 1
            vals_offs.append(arow['average_offs'])

    mean_ons = sum_ons / num_vals_ons
    list_mean_ons.append(mean_ons)
    dev_ons = []
    mean_offs = sum_offs / num_vals_offs
    list_mean_offs.append(mean_offs)
    dev_offs = []
    # 2. Find each values deviation from mean
    for val in vals_ons:
        dev_ons.append(val - mean_ons)
    for val in vals_offs:
        dev_offs.append(val - mean_offs)

    sq_sum_ons = 0
    sq_sum_offs = 0
    # 3. Square each deviation, and sum
    for dev in dev_ons:
        sq_sum_ons += dev ** 2
    for dev in dev_offs:
        sq_sum_offs += dev ** 2
    # 4. Divide the sum by n - 1, where n is # values in sample (variance)
    var_ons = sq_sum_ons / (num_vals_ons - 1)
    var_offs = sq_sum_offs / (num_vals_offs - 1)
    # 5. Square root variance -- this is std dev
    list_std_dev_ons.append(math.sqrt(var_ons))
    list_std_dev_offs.append(math.sqrt(var_offs))

df_rail['std_dev_ons'] = list_std_dev_ons
df_rail['mean_ons'] = list_mean_ons
df_rail['std_dev_offs'] = list_std_dev_offs
df_rail['mean_offs'] = list_mean_offs

df_rail.to_csv('test_all2.csv',index=False)

# # # # # # # # # # # # # # #
# Data Gen Pipeline for
# Travel Matrix on T
# # # # # # # # # # # # # # #
# 1. Getting Stops from certain lines
# for index, rrow in df_rail.iterrows():
#     if(rrow['time_period_name'] == 'VERY_EARLY_MORNING' and rrow['direction_id'] == 1 and rrow['day_type_name'] == 'weekday'):
#         if (rrow['route_id'] == 'Green'):
#             print(rrow['stop_id'])
            #print(rrow['stop_name'])
            #print()
# 2. Generating matrix from each stop to each stop
# dict_blue = json.load(open('blueline.json'))['stops']
# dict_red_a = json.load(open('redline-a.json'))['stops']
# dict_red_b = json.load(open('redline-b.json'))['stops']
# dict_orange = json.load(open('orangeline.json'))['stops']
# dict_green_e = json.load(open('greenline-e.json'))['stops']
# dict_green_d = json.load(open('greenline-d.json'))['stops']
# dict_green_c = json.load(open('greenline-c.json'))['stops']
# dict_green_b = json.load(open('greenline-b.json'))['stops']

# dict_dict = {
#     "blue":dict_blue,
#     "red-a":dict_red_a,
#     "red-b":dict_red_b,
#     "orange":dict_orange,
#     "green-e":dict_green_e,
#     "green-d":dict_green_d,
#     "green-c":dict_green_c,
#     "green-b":dict_green_b
# }

# dict_graph = json.load(open('graph.json'))
# dict_graph = {}
#all_stops = ['place-alsgr','place-armnl','place-babck','place-bckhl','place-bcnfd','place-bcnwa','place-bland','place-bndhl','place-boyls','place-brico','place-brkhl','place-brmnl','place-bucen','place-buest','place-buwst','place-bvmnl','place-chhil','place-chill','place-chswk','place-clmnl','place-coecl','place-cool','place-denrd','place-eliot','place-engav','place-fbkst','place-fenwd','place-fenwy','place-gover','place-grigg','place-haecl','place-harvd','place-hsmnl','place-hwsst','place-hymnl','place-kencl','place-kntst','place-lake','place-lech','place-lngmd','place-longw','place-mfa','place-mispk','place-newtn','place-newto','place-north','place-nuniv','place-pktrm','place-plsgr','place-prmnl','place-river','place-rsmnl','place-rvrwy','place-smary','place-sougr','place-spmnl','place-sthld','place-stplb','place-stpul','place-sumav','place-symcl','place-tapst','place-waban','place-wascm','place-woodl','place-wrnst','place-aport','place-aqucl','place-bmmnl','place-bomnl','place-gover','place-mvbcl','place-orhte','place-rbmnl','place-sdmnl','place-state','place-wimnl','place-wondl','place-mlmnl','place-north','place-ogmnl','place-rcmnl','place-rugg','place-sbmnl','place-state','place-sull','place-tumnl','place-welln','place-astao','place-bbsta','place-ccmnl','place-chncl','place-dwnxg','place-forhl','place-grnst','place-haecl','place-jaksn','place-masta','place-alfcl','place-andrw','place-asmnl','place-brdwy','place-brntn','place-chmnl','place-cntsq','place-davis','place-dwnxg','place-fldcr','place-harsq','place-jfk','place-knncl','place-nqncy','place-pktrm','place-portr','place-qamnl','place-qnctr','place-shmnl','place-smmnl','place-sstat','place-wlsta']

# def distance(line, origin, line_stops, stop, sofar, dir, curr_line, visited_lines):
#     if stop == 'place-xxxxx':
#         return
#     neighbor = 'inbound_neighbor' if dir == 'i' else 'outbound_neighbor'
#     time = 'inbound_time' if dir == 'i' else 'outbound_time'
#     dict_graph[line][origin][stop] = sofar
#     distance(line, origin, line_stops, line_stops[stop][neighbor], sofar + float(line_stops[stop][time]), dir, curr_line, visited_lines)
#     pot_trans = line_stops[stop]['transfer']
#     if pot_trans != 'none' and not pot_trans in visited_lines:
#         visited_lines.append(pot_trans)
#         distance(line, origin, dict_dict[pot_trans], stop, sofar, 'i', pot_trans, visited_lines)
#         distance(line, origin, dict_dict[pot_trans], stop, sofar, 'o', pot_trans, visited_lines)

# for line in dict_graph:
#     line_stops = dict_dict[line]
#     for stop in dict_graph[line]:
#         distance(line, stop, line_stops, stop, 0, 'i', line, [line])
#         distance(line, stop, line_stops, stop, 0, 'o', line, [line])

# print(json.dumps(dict_graph,indent=4))

# def calc_dist_with_origin(line, origin, start, dir, trans_from='none'):
#     data = dict_graph[line][origin]
#     line_stops = dict_dict[line]
#     next_stop = origin
#     sofar = 0
#     neighbor = 'inbound_neighbor' if dir == 'i' else 'outbound_neighbor'
#     time = 'inbound_time' if dir == 'i' else 'outbound_time'

#     while next_stop != 'place-xxxxx':
#         # check for pot transfers and prevent going back to prev transfer
#         if line_stops[next_stop]['transfer'] != 'none' and line_stops[next_stop]['transfer'] != trans_from:
#             transfer_line = dict_dict[line_stops[next_stop]['transfer']]
#             calc_dist_with_origin(transfer_line, next_stop, 'i', line)
#             calc_dist_with_origin(transfer_line, next_stop, 'o', line)
#             # now we assume that with next_stop knows all its distances
#             for t_stop in 

#         data[next_stop] = sofar
#         sofar += float(line_stops[next_stop][time])
#         next_stop = line_stops[next_stop][neighbor]

# blue_stops = dict_blue['stops']
# for line in dict_graph:
#     line_stops = dict_dict[line]
#     for origin in dict_graph[line]:
#         data = dict_graph[line][origin]
#         next_ib = origin
#         ib_sofar = 0
#         next_ob = origin
#         ob_sofar = 0

#         while next_ib != 'place-xxxxx':
#             if line_stops[next_ib]['transfer'] != 'none':
#                 transfer_line = dict_dict[line_stops[next_ib]['transfer']]
#                 # now we do it again...not using recursion cause im lazy rn
#                 trans_ib = next_ib
#                 trans_ib_so_far = ib_sofar
#                 trans_ob = next_ib
#                 trans_ob_so_far = ib_sofar
#                 while trans_ib != 'place-xxxxx':

#             data[next_ib] = ib_sofar
#             ib_sofar += float(line_stops[next_ib]['inbound_time'])
#             next_ib = line_stops[next_ib]['inbound_neighbor']

#         while next_ob != 'place-xxxxx':

#             data[next_ob] = ob_sofar
#             ob_sofar += float(line_stops[next_ob]['outbound_time'])
#             next_ob = line_stops[next_ob]['outbound_neighbor']

# def find_times(line_stops, graph):
#     for origin in all_stops:
#         next_ib = origin
#         ib_sofar = 0
#         next_ob = origin
#         ob_sofar = 0

#         while next_ib != 'place-xxxxx':
#             if line_stops[next_ib]['transfer'] != 'none':

#             graph[origin][next_ib] = ib_sofar
#             ib_sofar += float(line_stops[next_ib]['inbound_time'])
#             next_ib = line_stops[next_ib]['inbound_neighbor']

#         while next_ob != 'place-xxxxx':
#             graph[origin][next_ob] = ob_sofar
#             ob_sofar += float(line_stops[next_ob]['outbound_time'])
#             next_ob = line_stops[next_ob]['outbound_neighbor']

#     print(json.dumps(graph,indent=4))    
#     return graph

# Testing Google Maps' Limits
# origins = ""
# for index, rrow in df_rail_stops.iterrows():
#     #origins += ("|"+str(rrow['stop_lat']) + ',' + str(rrow['stop_lon']))
#     dests = ""
#     for index, crow in df_rail_stops.iterrows():
#         if str(crow['stop_id']) == str(rrow['stop_id']):
#             continue
#         dests += ("|" + str(crow['stop_lat']) + ',' + str(crow['stop_lon']))

#     p = {
#         "mode":"transit", 
#         "transit_mode":"rail",
#         "origins":str(rrow['stop_lat']) + ',' + str(rrow['stop_lon']),
#         "destinations":dests,
#         "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
#     }
#     response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
#     print(response.json())

#d = {}
# for index, rrow in df_rail.iterrows():
#     found = False
#     # only need to look at each one once
#     if rrow['time_period_name'] == "EARLY_AM":
#         if '\'' + str(rrow['stop_id']) + '\'' in df_stops['stop_id'].tolist():
#             d[str(rrow['stop_id'])] = str(rrow['stop_name'])
#         # for index, srow in df_stops.iterrows():
#         #     if str(rrow['stop_id']) == str(srow['stop_id']):
#         #         #print("Found " + str(rrow['stop_id']))
#         #         found = True
#         #         break
#         # if not found:
#         #     #print("Didn't find " + str(rrow['stop_id']))
#         #     d[str(rrow['stop_id'])] = str(rrow['stop_name'])
# for key in d:
#     print('Couldn\'t find: ' + key + ', ' + d[key])
# df_bus = df_bus[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
# df_rail = df_rail[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
# df_bus.to_csv('MBTA_Bus_Stops.csv', index=False)
# df_rail.to_csv('MBTA_Rail_Stops.csv', index=False)

# sum_ons_bus = 0
# sums = {
# "VERY_EARLY_MORNING" : 0,
# "EARLY_AM" : 0,
# "AM_PEAK" : 0,
# "MIDDAY_BASE" : 0,
# "MIDDAY_SCHOOL" : 0,
# "PM_PEAK" : 0,
# "EVENING" : 0,
# "LATE_EVENING" : 0,
# "NIGHT" : 0,
# }
# for index, row in df_bus[['average_ons', 'average_offs', 'time_period_name']].iterrows():
#     sums[row['time_period_name']] += row['average_ons']

# list_odds = []
# list_odds_offs = []
# for index, row in df_bus[['stop_name', 'average_ons', 'average_offs', 'time_period_name']].iterrows():
#     list_odds.append(row['average_ons'] / sums[row['time_period_name']])
#     list_odds_offs.append(row['average_offs'] / sums[row['time_period_name']])
#     print(row['stop_name'] + ', ' + row['time_period_name'] + ', ' + str(list_odds[-1]))
#     print(row['stop_name'] + ', ' + row['time_period_name'] + ', ' + str(list_odds_offs[-1]))

# print(list_odds)
# print(len(list_odds))
# print(len(df_rail[['stop_name']]))
# df_bus['odds_on'] = list_odds
# df_bus['odds_off'] = list_odds_offs
# df_bus.to_csv('test.csv',index=False)

# for key in sums:
#     if 'ons' in key:
#         print("=============ons================\n" + key + ":\n" + str(sums[key]) + "\n" + str(float(sums[key] / sum_ons_bus)))
#     else:
#         print("==============offs===============\n" + key + ":\n" + str(sums[key]) + "\n" + str(float(sums[key] / sum_offs_bus)))

# print(sum_ons_bus)
# print(sum_offs_bus)

# sum_ons_bus = 0
# sum_offs_bus = 0
# for index, row in df_bus[['average_ons', 'average_offs']].iterrows():
#     sum_ons_bus += row['average_ons']
#     sum_offs_bus += row['average_offs']

# print(sum_ons_bus)
# print(sum_offs_bus)

#check if we can actually find all these locations or if some are "NOT_FOUND"
# df_rail = pd.read_csv('MBTA_Rail_Stops.csv')
# df_bus = pd.read_csv('MBTA_Bus_Stops.csv')

# for index,row in df_rail[['stop_name','route_name']].iterrows():
#     p = {
#             "mode":"transit", 
#             "transit_mode":"rail",
#             "origins":row['stop_name'] + " Station " + row['route_name'] + " MBTA",
#             "destinations":"Alewife Red Line MBTA", # dummy which we know we can find
#             "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
#     }
#     response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
#     if response.json()['rows'][0]['elements'][0]['status'] == 'NOT_FOUND':
#         print("Didn't find: " + row['stop_name'] + " " + row['route_name'] + " MBTA")

# print("\nBUS\n")
# for index,row in df_bus[['stop_name','route_name']].iterrows():
#     p = {
#             "mode":"transit", 
#             "origins":row['stop_name'] + " Station " + row['route_name'] + " MBTA",
#             "destinations":"Alewife Red Line MBTA", # dummy which we know we can find
#             "key":"AIzaSyCJ3bMTL8NA1UmL3D-ZyWH-0rx98q71vqQ" 
#     }
#     response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params = p)
#     if response.json()['rows'][0]['elements'][0]['status'] == 'NOT_FOUND':
#         print("Didn't find: " + row['stop_name'] + " " + row['route_name'] + " MBTA")