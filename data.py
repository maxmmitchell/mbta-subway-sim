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

df_rail = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df_bus = pd.read_csv('MBTA_Bus_Ridership_by_Time_Period.csv')

df_bus = df_bus[['stop_name', 'route_name']]
df_bus.to_csv('MBTA_Bus_Stops.csv', index=False)

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
