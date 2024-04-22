# `MBTA Subway Sim`
*A simulator of outages and station additions to the MTA subway*

## What does `MBTA Subway Sim` do?
`MBTA Subway Sim` simulates the effects of station addition and subtractions on the MBTA subway. It anticipates how riders might be impacted using historical data. It takes into account week-wise date and time-of-day-wise time variance in ridership. `MBTA Subway Sim`, when run, fills the folder `sim_out` (which must exist) with the following files:
- `log.json`: log of the impacts of the user-described change to the subway system. In the case of subtraction, the keys represent the stop which was used to replace the removed station, and the value is a list of the change(s) in total ride time this caused, in minutes. In the case of addition, the keys represent stations whose riders in the original model were "poached" by the new stop, and the value is a list of the change(s) in total ride time this caused, in minutes.
- `map.json`: recalculation of the time-matrix contained in `rail_map.json`
- `model.json`: recomputed model based on the model which was fed into the simulation, accounting for the changes.

## How do I use `MBTA Subway Sim`?
`python3 simulation.py [OPTIONS]`
- ``

## What files are here?
- `data.py`: working file for processing data. Used for intermediate phases but more or less irrelevant now.
- `genotype.py`: class representing an individual of our model, for genetic algorithm purposes.
- `main.py`: runs the actual simulation, and interacts with the user.
- `simulation.py`: set of functions which act as the logic of simulating adding and removing stops.
- `train.py`: script to train a model based on many pre-generated models.
- `genModels.sh`: script to generate models. Somewhat hacky.

## How was `MBTA Subway Sim` made?
`MBTA Subway Sim` was created by Max Mitchell for his Master's project at Tufts University across the 2023-2024 school year. 

## 
Special thanks to Richard Townsend, my advisor. Liping Liu and Shan Jiang, for providing advice in a field which was new to me.
