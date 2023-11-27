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

df_rail = pd.read_csv('MBTA_Rail_Stop_Cords.csv')
df_bus = pd.read_csv('MBTA_Bus_Stop_Cords.csv')

df_bus = df_bus[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
df_rail = df_rail[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
df_bus.to_csv('MBTA_Bus_Stops.csv', index=False)
df_rail.to_csv('MBTA_Rail_Stops.csv', index=False)

# sum_ons_rail = 0
# sum_offs_rail = 0
# for index, row in df_rail[['average_ons', 'average_offs']].iterrows():
#     sum_ons_rail += row['average_ons']
#     sum_offs_rail += row['average_offs']

# print(sum_ons_rail)
# print(sum_offs_rail)

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