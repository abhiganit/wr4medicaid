import model
import numpy as np
import pandas as pd
from itertools import product

# create input criteria for scenarios:
## Choose age_upper_bound:
state = 'Alabama'
age_upper_bound = 64# 55 or 64

## This one should just work.
def get_inputs(state, age_upper_bound):
    atrisk = [20272000, 36188000]  # Change this such that I grab the right thing. Use CBPP.
    reporting_rate = [0.18, 0.28, 0]
    if age_upper_bound ==64:
        automatic_exemption = [1 - 0.506221869, 0]  # 64
    else:
        atrisk = [0.796 * i for i in atrisk]
        automatic_exemption = [1 - 0.475364278, 0]  # 55
    return atrisk, reporting_rate, automatic_exemption

def get_age_based_inputs(age_upper_bound):
    if age_upper_bound == 55:
        # For 19--55 age-group
        agerange = [19, 55]
        ages = ['19 to 25 years', '26 to 34 years', '35 to 44 years', '45 to 54 years']
        agesD = ['15-24', '25-34', '35-44', '45-54']
    else:
        # For 19--64 age-group
        agerange = [19,65]
        ages = ['19 to 25 years', '26 to 34 years', '35 to 44 years', '45 to 54 years', '55 to 64 years']
        agesD = ['15-24','25-34','35-44','45-54','55-64']
    return agerange, ages, agesD

agerange0, ages0, agesD0 = get_age_based_inputs(age_upper_bound)

# Same data can't be used to get what I want, though I can easily now
pop_model = model.PopulationModel('data/np2023.csv',agerange0)
# For each state, for population I can use another data to get population at state-level prpoortionally.

## This is one big thingy that is working.
ins_model = model.InsuranceModel('data/S2701 Selected Characteristics 2023.xlsx', ages0,'Alabama')

death_model = model.DeathRateModel('data/Mortality Data 2021-2022.csv',agesD0)