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

df = pd.read_csv('MBTA_Rail_Ridership_by_Time_Period.csv')
df = df[['stop_name', 'route_name']]
df.to_csv('MBTA_stops.csv', index=False)
