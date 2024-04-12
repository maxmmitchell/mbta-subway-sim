# `MBTA Subway Sim`
*A simulator of outages and station additions to the MTA subway*

## What does `MBTA Subway Sim` do?
`MTA Subway Sim` simulates the effects of station addition and removals on the MBTA subway. It anticipates how riders might be impacted using historical data. It takes into account week-wise date and time-of-day-wise time variance in ridership.

## How do I use `MBTA Subway Sim`?

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
