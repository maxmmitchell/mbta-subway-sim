# `MBTA Subway Sim`
*A simulator of outages and station additions to the MBTA subway*

## What does `MBTA Subway Sim` do?
`MBTA Subway Sim` simulates the effects of station addition and subtractions on the MBTA subway. It anticipates how riders might be impacted using historical data. It takes into account week-wise date and time-of-day-wise time variance in ridership. `MBTA Subway Sim`, when run, fills the folder `sim_out` (which must exist) with the following files:
- `log.json`: log of the impacts of the user-described change to the subway system. In the case of subtraction, the keys represent the stop which was used to replace the removed station, and the value is a list of the change(s) in total ride time this caused, in minutes. In the case of addition, the keys represent stations whose riders in the original model were "poached" by the new stop, and the value is a list of the change(s) in total ride time this caused, in minutes.
- `map.json`: recalculation of the time-matrix contained in `rail_map.json`
- `model.json`: recomputed model based on the model which was fed into the simulation, accounting for the changes.

## How do I use `MBTA Subway Sim`?
`python3 simulation.py [OPTIONS]`
- `--interactive`, `-i` 
        Run the simulation in interactive mode. Feature still in development.
- `--add/--subtract`, `-a/-s` 
        Elect to add or remove a station. It is required to select one, and only one.
- `--station TEXT`
        Station(s) for either addition or subtraction, by their `stop_id`. In subtraction mode, this station is removed. In addition, these station(s) indicate which station(s) to add the new station between. If only one station is provided in addition mode, it is assumed that the new station is to be added at the end of the line.
- `--latitude FLOAT`
        Latitude to place new station at.
- `--longitude FLOAT`
        Longitude to place new station at.
- `--line TEXT`
        Line to place new stop on. Valid options are: red-a, red-b, blue, orange, green-b, green-c, green-d, and green-e.
- `--from-file TEXT`
        Set a different directory from which to pull the input model, and map files. Paths are assumed local to current working directory.
- `--output TEXT`
        Set a different directory in which to deposit the output log files. Paths are assumed local to current working directory.
- `--help`
        Display the above options and descriptions.
- `--name`
        Set a name for a newly added station. Must be five letters long, and be unique.

## How do I find the `stop_id` for the station I want?
Check `MBTA_Rail_Stops.csv`. A simple grep for the common stop name, or address, should turn up the appropriate row with the `stop_id`.

## How do I know which line to use?
Most stops are on the line expected of them, e.g., Forest Hills is on orange, Wonderland is on blue, etc. Things get funky with the green and red line, which are broken up corresponding to their branches. For the red line, stations from Alewife to Ashmont is on red-a, and stations from JFK to Braintree is on red-b. For the green line, TODO

## What files are here?
- `data.py`: working file for processing data. Used for intermediate phases but more or less irrelevant now.
- `genotype.py`: class representing an individual of our model, for genetic algorithm purposes.
- `main.py`: runs the actual simulation, and interacts with the user.
- `simulation.py`: set of functions which act as the logic of simulating adding and removing stops.
- `train.py`: script to train a model based on many pre-generated models.
- `genModels.sh`: script to generate models. Somewhat hacky.
- `/sim_out_default`: default location for simulation output files.
- `/sim_in_default/`: default location for simulation start-up files.
- - `full_model_1.json`: TODO DESCRIBE MODEL FILE
- - `map.json`: distance matrix representing the time from each station to every other station.
- - `red-a.json, red-b.json, blue.json, orange.json, green-e.json, green-d.json, green-c.json, green-b.json`: representations of the layout of each line. branches get their own file, and to avoid duplication, common set of track is only represented once, as this representation cares only about stop-to-stop times. `red-a.json` and `green-e.json` get the bulk of it; see official write-up for more details.
- `/out_add_ex/`: example of adding a station.
- `/out_sub_ex/`: example of subtracting a station. 

## How was `MBTA Subway Sim` made?
`MBTA Subway Sim` was created by Max Mitchell for his Master's project at Tufts University across the 2023-2024 school year. It has two parts; the model, and the simulation. The model is a genetic model representing a full set a rides on a given day, inferring routes based on historical ridership traffic data available on the MBTA's open data portal. the simulation expands on this model, taking as an input a change to the subway structure, and simulating the impact on ridership for current riders.

## Future Work Ideas TODO EDIT THIS
- Interactive Mode
- Improving the model/simulation, lots of tuning to be done.
- Manifest documents in out directories describing line changes
- Allow for outages/subtraction to be only for a set time range (e.g., AM_PEAK only, or PM-MIDNIGHT, etc.)

## Gratitude
Special thanks to Richard Townsend, my advisor. Liping Liu and Shan Jiang, for providing advice in a field which was new to me.
