import pandas as pd
import numpy as np
import random

perfect_sequences = []
numbers = 0
iterations = 0

while numbers < 4: 
    iterations += 1
    #print("This is iteration {}".format(iterations))
    trials = ["E"] * 14 + ["D"] * 14
    random.shuffle(trials)

    EE, ED, DE, DD = 0, 0, 0, 0

    for i in range(len(trials)-1):
        if trials[i] + trials[i + 1] == "EE":
            EE +=1
        if trials[i] + trials[i + 1] == "ED":
            ED +=1
        if trials[i] + trials[i + 1] == "DE":
            DE +=1
        if trials[i] + trials[i + 1] == "DD":
            DD +=1

    if (EE == 6 and DD == ED == DE == 7) or (DD == 6 and EE == ED == DE == 7) or (ED == 6 and EE == DD == DE == 7) or (DE == 6 and EE == ED == DD == 7):
        print("Sequence: ", ''.join(trials))
        print("EE: ", EE, "ED: ", ED, "DE: ", DE, "DD: ", DD)
        perfect_sequences.append(trials)
        numbers += 1

for sequence in perfect_sequences:
    print(sequence, "\n")