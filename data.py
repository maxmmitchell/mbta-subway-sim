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

df_rail = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_bus = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')

# df_bus = df_bus[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
# df_rail = df_rail[['stop_name', 'stop_lat', 'stop_lon', 'Routes']]
# df_bus.to_csv('MBTA_Bus_Stops.csv', index=False)
# df_rail.to_csv('MBTA_Rail_Stops.csv', index=False)

sum_ons_bus = 0
sums = {
"very_early_morning_ons" : 0,
"early_am_ons" : 0,
"am_peak_ons" : 0,
"midday_base_ons" : 0,
"midday_school_ons" : 0,
"pm_peak_ons" : 0,
"evening_ons" : 0,
"late_evening_ons" : 0,
"night_ons" : 0,
}
for index, row in df_rail[['average_ons', 'time_period_name']].iterrows():
    sums[row['time_period_name'].lower() + '_ons'] += row['average_ons']

list_odds = []
for index, row in df_rail[['stop_name', 'average_ons','time_period_name']].iterrows():
    list_odds.append(row['average_ons'] / sums[row['time_period_name'].lower() + '_ons'])
    print(row['stop_name'] + ', ' + row['time_period_name'] + ', ' + str(list_odds[-1]))

df_rail[['odds_station_time_on']] = list_odds
df_rail.to_csv('test.csv',index=False)

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