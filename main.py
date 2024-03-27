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
import os, fnmatch

# # # # # # # # # # # # # #
# Breeding Generations
# of Models
# # # # # # # # # # # # # #
# gen = 0
# for i in range(1):
#     # 1. Read in Models for Current Generation
#     next_gen = fnmatch.filter(os.listdir('.'), 'model-gen'+str(gen) +'*.json')
#     new_models = []
#     for m in next_gen:
#         print(m)
#         model = g.Genotype(False)
#         model.from_file(m)
#         # 2. Calculate Fitness -- Report
#         fitness = model.fitness_rideset('rail')
#         new_models.append([fitness, m, model])
#     new_models.sort()
#     for fitness, m, model in new_models:
#         print(str(fitness) + ': ' + m)
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


