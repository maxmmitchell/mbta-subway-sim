###############################################################
#    getdata.py
#        A quick and dirty way to snag some data
#        using SOQL and HTTP gets.
#    Fall 2023
#    maxwell.mitchell@tufts.edu
#    Master's Capstone Project
###############################################################

import requests
import json

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

p = {   
        "$select": "station_complex, station_complex_id where transit_timestamp = '2023-10-01T00:00:00.000' and payment_method = 'omny' limit 140000" # should be roughly 7 days worth
    }
response = requests.get("https://data.ny.gov/resource/wujg-7c2s.json", params = p)
# print(response.status_code) # for debugging
jprint(response.json())