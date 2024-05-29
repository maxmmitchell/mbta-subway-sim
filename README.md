# `MBTA Subway Sim`
*A simulator of outages and station additions to the MBTA subway*

## What does `MBTA Subway Sim` do?
`MBTA Subway Sim` simulates the effects of station addition and subtractions on the MBTA subway. It anticipates how riders might be impacted using historical data. It takes into account week-wise date and time-of-day-wise time variance in ridership. `MBTA Subway Sim`, when run, fills the folder `sim_out` (or a user-described folder, which must exist) with the following files:
- `log.json`: log of the impacts of the user-described change to the subway system. In the case of subtraction, the keys represent the stop which was used to replace the removed station, and the value is a list of the change(s) in total ride time this caused, in minutes. In the case of addition, the keys represent stations whose riders in the original model were "poached" by the new stop, and the value is a list of the change(s) in total ride time this caused, in minutes.
- `manifest.txt`: manifest describing the change(s) made to the subway system by the user.
- `map.json`: recalculation of the time-matrix contained in `rail_map.json`
- `model.json`: recomputed model based on the model which was fed into the simulation, accounting for the changes.
- `red-a.json, red-b.json, blue.json, orange.json, green-e.json, green-d.json, green-c.json, green-b.json`: recomputed map of the MBTA for each line.
The output can itself then be fed back into the simulation, allowing for iterative changes to the MBTA to be simulated. Or, run the simulation in interactive mode to apply many changes simultaneously. Note that in interactive mode, the simulation will appear to hang after validating input and applying the change. This is normal, and will be quite long with the full-size model. For the `log.json` file in interactive mode, an additional wrapper around the normal log structure organizes each log by each action (add/sub) that was made before log was written to file.

## How do I use `MBTA Subway Sim`?
`python3 simulation.py [OPTIONS]`
- `--interactive`, `-i` 
        Run the simulation in interactive mode. 
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

Examples:

`python3 simulation.py -i`
Run the simulation in interactive mode.

`python3.9 simulation.py -s --station place-davis`
Simulate the subtraction of the Davis Square station from the Red line.

`python3.9 simulation.py -a --station place-harsq --station place-portr --latitude 42.380869 --longitude -71.119685 --line red-a --output /out_add_ex_full/ --from-file /sim_in_full/ --name lesly`
Using the full-size model, simulate the addition of a station named `place-lesly` to the Red line between Harvard Square and Porter Square stations, at the coordinates `(42.380869, -71.119685)`. Send the output of this to the directory `/out_add_ex_full/`.

## How do I find the `stop_id` for the station I want?
Check `MBTA_Rail_Stops.csv`. A simple grep for the common stop name, or address, should turn up the appropriate row with the `stop_id`. Note that while `MBTA_Rail_Stops.csv` is a handy guide for finding information on stations, it is _not_ the resource used by the simulation to determine whether or not stops exist -- for that, please see `map.json`.

## How do I know which line to use?
Most stops are on the line expected of them, e.g., Forest Hills is on orange, Wonderland is on blue, etc. Things get funky with the green and red line, which are broken up corresponding to their branches. For the red line, stations from Alewife to Ashmont is on red-a, and stations from JFK to Braintree is on red-b. For the green line, green-e contains stations from Lechmere to Heath St., green-d contains stations from Kenmore to Riverside, green-c contains stations from Kenmore to Cleveland Circle, and green-b contains stations from Kenmore to Boston College.

## What files are here?
- `data.py`: working file for processing data. Used for intermediate phases but more or less irrelevant now.
- `genotype.py`: class representing an individual of our model, for genetic algorithm purposes.
- `simulation.py`: contains all logic for the simulation, as well as for user-interactivity.
- `train.py`: script to train a model based on many pre-generated models.
- `genModels.sh`: script to generate models. Somewhat hacky.
- `MBTA_*.csv`: various files containing data from the MBTA.
- `faregate_entries_nov2023.csv`: modern data from the MBTA on faregate entries for November, 2023. To be used for testing the GLX simulation.
- `writeup.pdf`: semi-formal write-up of Max Mitchell's original project.
- `/sim_out/`: default location for simulation output files.
- `/sim_in_default/`: default location for simulation start-up files.
- - `model.json`: 1/60th scale-model representing a day's worth of MBTA rides. scaled down for speed purposes.
- - `map.json`: distance matrix representing the time from each station to every other station.
- - `red-a.json, red-b.json, blue.json, orange.json, green-e.json, green-d.json, green-c.json, green-b.json`: representations of the layout of each line. branches get their own file, and to avoid duplication, common set of track is only represented once, as this representation cares only about stop-to-stop times. `red-a.json` and `green-e.json` get the bulk of it; see official write-up for more details.
- - `/sim_in_full/`: same as `/sim_in_default/`, except contains a full-size model instead of a scale one. Note that due to their large size, all full-size models (both in this input directory, and in the examples) are compressed using Gzip.
- `/examples/`: directory of examples of various outputs from different ways to use the simulation.
- - `/out_add_ex/`: example of adding a station.
- - `/out_sub_ex/`: example of subtracting a station. 
- - `/out_i_ex/`: example of using the interactive mode to make multiple modifications.
- - `/out_add_ex_full/`: example of adding a station, with the full-size model.
- - `/out_sub_ex_full/`: example of subtracting a station, with the full-size model. 
- - `/out_test_glx/`: output from a test recreating the Green Line Extension project using the simulation.
- `/model_bin/`: folder containing compressed models used in the model training process.

## How was `MBTA Subway Sim` made?
`MBTA Subway Sim` was created by Max Mitchell for his Master's project at Tufts University across the 2023-2024 school year. It has two parts; the model, and the simulation. The model is a genetic model representing a full set a rides on a given day, inferring routes based on historical ridership traffic data available on the MBTA's open data portal. the simulation expands on this model, taking as an input a change to the subway structure, and simulating the impact on ridership for current riders. 

## Future Work
`MBTA Subway Sim` has many exciting avenues remaining for future development and work. Please review `writeup.pdf`'s Future Work section for more details, and `CONTRIBUTING.md` for guidelines on adding code to this repo.

## Acknowledgments
I'd like to express my gratitude to a number of people who helped me on this project. To Richard Townsend, my advisor, who provided lots of support, encouragement, and feedback from the beginning through the end. To Liping Liu and Shan Jiang, for providing advice in a field which was new to me. To my brother, who reviewed my design document and pushed me to try something new. And finally, to all my friends and family, for everything.
