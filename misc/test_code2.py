import pandas as pd
import random

stimuli_df = pd.read_excel('passages.xlsx')
subject_group = random.choice([1,2])

print(stimuli_df)
# Assuming stimuli_df is already loaded
# Group by valence
valence_groups = stimuli_df.groupby('VAL')

# Initialize empty DataFrames for each subset
EN_subset = pd.DataFrame()
NL_subset = pd.DataFrame()

# Distribute passages for each valence group to ensure balance
for valence, group in valence_groups:
    # Shuffle the group to randomize distribution
    shuffled_group = group.sample(frac=1).reset_index(drop=True)
    midpoint = len(shuffled_group) // 2  # Find the midpoint to split evenly
    
    # Distribute evenly between L1 and L2
    EN_subset = pd.concat([EN_subset, shuffled_group[:midpoint]])
    NL_subset = pd.concat([NL_subset, shuffled_group[midpoint:]])

# Shuffle the subsets to randomize the order after distribution
EN_subset = EN_subset.sample(frac=1).reset_index(drop=True)
NL_subset = NL_subset.sample(frac=1).reset_index(drop=True)

EN_subset = EN_subset.drop(columns=["NLP", "NLT"], axis = 1)
NL_subset = NL_subset.drop(columns=["ENP", "ENT"], axis = 1)

print(EN_subset.head())
print(NL_subset.head())