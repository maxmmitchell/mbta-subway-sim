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

df_rail = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_bus = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')
df_rail_stops = pd.read_csv('MBTA_Rail_Stops.csv')
df_bus_stops = pd.read_csv('MBTA_Bus_Stops.csv')
df_stops = pd.read_csv('stops-20190808-modified.csv')

# # # # # # # # # # # # # # #
# Data Gen Pipeline for
# Travel Matrix on T
# # # # # # # # # # # # # # #
# 1. Getting Stops from certain lines
for index, rrow in df_rail.iterrows():
    if(rrow['time_period_name'] == 'VERY_EARLY_MORNING' and rrow['direction_id'] == 1 and rrow['day_type_name'] == 'weekday'):
        if (rrow['route_id'] == 'Green'):
            print(rrow['stop_id'])
            print(rrow['stop_name'])
            print()
# 2. Generating matrix from each stop to each stop
# dict_blue = json.load(open('blueline.json'))
# dict_red_a = json.load(open('redline-a.json'))
# dict_red_b = json.load(open('redline-b.json'))
# dict_orange = json.load(open('orangeline.json'))
# dict_green_e = json.load(open('greenline-e.json'))
# dict_green_d = json.load(open('greenline-d.json'))
# dict_green_c = json.load(open('greenline-c.json'))
# dict_green_b = json.load(open('greenline-b.json'))

# dict_graph = json.load(open('graph.json'))
#dict_graph = {}
#all_stops = ['place-alsgr','place-armnl','place-babck','place-bckhl','place-bcnfd','place-bcnwa','place-bland','place-bndhl','place-boyls','place-brico','place-brkhl','place-brmnl','place-bucen','place-buest','place-buwst','place-bvmnl','place-chhil','place-chill','place-chswk','place-clmnl','place-coecl','place-cool','place-denrd','place-eliot','place-engav','place-fbkst','place-fenwd','place-fenwy','place-gover','place-grigg','place-haecl','place-harvd','place-hsmnl','place-hwsst','place-hymnl','place-kencl','place-kntst','place-lake','place-lech','place-lngmd','place-longw','place-mfa','place-mispk','place-newtn','place-newto','place-north','place-nuniv','place-pktrm','place-plsgr','place-prmnl','place-river','place-rsmnl','place-rvrwy','place-smary','place-sougr','place-spmnl','place-sthld','place-stplb','place-stpul','place-sumav','place-symcl','place-tapst','place-waban','place-wascm','place-woodl','place-wrnst','place-aport','place-aqucl','place-bmmnl','place-bomnl','place-gover','place-mvbcl','place-orhte','place-rbmnl','place-sdmnl','place-state','place-wimnl','place-wondl','place-mlmnl','place-north','place-ogmnl','place-rcmnl','place-rugg','place-sbmnl','place-state','place-sull','place-tumnl','place-welln','place-astao','place-bbsta','place-ccmnl','place-chncl','place-dwnxg','place-forhl','place-grnst','place-haecl','place-jaksn','place-masta','place-alfcl','place-andrw','place-asmnl','place-brdwy','place-brntn','place-chmnl','place-cntsq','place-davis','place-dwnxg','place-fldcr','place-harsq','place-jfk','place-knncl','place-nqncy','place-pktrm','place-portr','place-qamnl','place-qnctr','place-shmnl','place-smmnl','place-sstat','place-wlsta']

# graph_stops = dict_graph['blue']
# blue_stops = dict_blue['stops']
# for origin in graph_stops:
#     data = graph_stops[origin]
#     next_ib = blue_stops[origin]['inbound_neighbor']
#     ib_sofar = 0
#     next_ob = blue_stops[origin]['outbound_neighbor']
#     ob_sofar = 0

#     while next_ib != 'place-xxxxx':
#         ib_sofar += float(blue_stops[next_ib]['inbound_time'])
#         data[next_ib] = ib_sofar
#         next_ib = blue_stops[next_ib]['inbound_neighbor']

#     while next_ob != 'place-xxxxx':
#         ob_sofar += float(blue_stops[next_ob]['outbound_time'])
#         data[next_ob] = ob_sofar
#         next_ob = blue_stops[next_ob]['outbound_neighbor']

# print(json.dumps(dict_graph,indent=4))

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