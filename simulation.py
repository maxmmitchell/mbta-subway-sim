# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    simulation.py
#       Models impacts of changes to a rail system.
#    Spring 2024
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Consider a ride starting at X, call the other stop Y. Assign more granular locations beyond X and Y. Select a random location (pair of coordinates) such that the location:
#   - is at most a twenty minute walk from the respective stop, and at least a five minute walk.
#   - is not nearer any other stop A than it is to X, assuming A and X both service Y (and vice-versa, for Y).
# Call these coordinates CX and CY.

# Stop Subtraction:
# 1. User selects a valid stop to remove from the MBTA. Call this stop X. Generate granular locations for all rides involving X.
# 2. All rides which include X must be re-routed. Find stop Z, which is connected to Y and is nearest to CX.

# Stop Addition:
# 1. User inputs coordinates and a valid line(s) to add the stop to. Call this stop N. 
# 2. Find the nearest stops to N (which N may poach riders from). Call these stops Pi such that for all Pi:
#   A. N is less than a 40 minute walk away. Ergo, N is a reasonable walking distance from the ride’s granular location.
# 3. For all Pi find all rides that include at least one Pi. Generate granular locations for them. 
# 4. Then, from this set of rides, find all poachable riders, Ri  such that for each:
#   A. The other end of their route, O, is serviceable by N 
#   B. Using N is more efficient
#       i. Calculate walk time to N and walk time to Pi
#       ii. Calculate transit time for both. 
#           a. If N is between two existing stops:
#
#               1 -- N -- 2 -- O
#	
#               - Calculate the transit ride time from 1 to O (or vice versa depending on ride)
#               - Calculate the transit ride time from 2 to O (or vice versa)
#               - Compute the difference. Add to the transit ride time from 2 to O a fraction of the difference based on how close N is to 2 vs. 1.
#           b. If N is expanding a line:
#
#               N -- 2 -- O
#
#               - Calculate the transit ride time from 2 to O (or vice versa)
#               - Add based on the distance from N to 2
#               Note: For both of these, depending on line, will need to look at how long the 
#                     subway generally takes to travel such distance. This can probably be a 
#                     precalculated constant for each line just as a MPH or something.
#       iii. Sum walk and transit time. Walk time should be weighted somewhat to favor less walking in the overall route.
# 5. For all Ri, replace Pi with N.
#
# At this point, ridership metrics can be recalculated. 
# For now, we assume no impact of a new stop on the rest of the route, e.g.:
#
#     1 -- 2 -------- O     ->     1 -- 2 -       - O
#                                           \   /
#                                            | |
#                                             N
# Is not a concern.