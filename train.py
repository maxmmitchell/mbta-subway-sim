# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    train.py
#        
#    Spring 2023
#    Max Mitchell
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import csv
import genotype as g
import os, fnmatch
import random

# # # # # # # # # # # # # #
# Breeding Generations
# of Models
# # # # # # # # # # # # # #
gen = 0
prev_models = []
for i in range(6):
    # 1. Read in Models for Current Generation
    next_gen = fnmatch.filter(os.listdir('.'), 'model-gen'+str(gen) +'*.json')
    curr_models = prev_models
    prev_models = []
    for m in next_gen:
        model = g.Genotype(False)
        model.from_file(m)
        # 2. Calculate Fitness -- Report
        fitness = model.fitness_rideset('rail')
        curr_models.append([fitness, m, model])
    curr_models.sort()
    for fitness, m, model in curr_models:
        print(str(fitness) + ': ' + m)
    # 3. Mutate, Crossover, and Replace from Pool
    # eliminate 
    curr_models = curr_models[0:5]
    # create new individuals to replace
    mutate = True
    for fitness, m, model in curr_models:
        new_model = model
        if mutate or model == curr_models[-1]:
            print("Mutating: " + m)
            new_model = model.mutation()
            new_name = m + "_mutation_gen" + str(gen)
        else:
            # select random partner
            other = [fitness, m, model]
            while other[1] == m:
                other = curr_models[random.randrange(0, len(curr_models))]
            print("Crossing " + m + " over " + other[1])
            new_model = model.crossover(other[2])
            new_name = m + "_crossover_" + other[1] + "_gen" + str(gen)
        mutate = not mutate
        prev_models.append([new_model.fitness_rideset('rail'), new_name, new_model])
        prev_models.append([fitness, m, model])
    gen += 1 
    # 4. Repeat
# 5. Export the Best
print("Winners: ")
for i in range(3):
    print(str(prev_models[i][0]) + ' : ' + prev_models[i][1])
    file = open('model_trained_' + str(i), 'w')
    print(prev_models[i][2].json_print(), file=file)
    file.close()
