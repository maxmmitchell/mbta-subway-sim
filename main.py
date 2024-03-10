# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    main.py
#        
#    Fall 2023
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import csv
import genotype as g

# # # # # # # # # # # # # #
# Breeding Generations
# of Models
# # # # # # # # # # # # # #
# 1. Read in Models for Current Generation
# 2. Calculate Fitness -- Report
# 3. Mutate, Crossover, and Replace from Pool
# 4. Repeat

geno = g.Genotype()
print(geno.json_print())
# genoFromFile = g.Genotype(False)
# genoFromFile.from_file('primitive_demo.json')
#print(genoFromFile.json_print())
# print(genoFromFile.fitness())

# geno1 = g.Genotype()
# geno2 = g.Genotype()
# print(geno1.json_print())
# print(geno2.json_print())
# mutated1 = geno1.mutation()
# print(mutated1.json_print())
# cross12 = geno1.crossover(geno2)
# print(cross12.json_print())


