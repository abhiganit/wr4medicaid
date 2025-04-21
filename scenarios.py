from numpy.f2py.crackfortran import endifs

import model
import numpy as np
import pandas as pd
from itertools import product

# create input criteria for scenarios:
## Choose age_upper_bound:
age_upper_bound = 64# 55 or 64

def get_inputs(age_upper_bound):
    atrisk = [20272000, 36188000]  # Expansion, Total
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


def get_morbidity_results(pop, prev, uncontrol, current_coverage, updated_coverage, elevated_risk):
    current = uncontrol * prev * pop
    risk_multiplier = (updated_coverage + elevated_risk*(1-updated_coverage)) / (current_coverage + elevated_risk*(1-current_coverage))
    updated = risk_multiplier * current
    return current, updated, updated-current


# Run simulation for age-group 19-65
# Get values for age-group 19--65
agerange0, ages0, agesD0 = get_age_based_inputs(age_upper_bound)
pop_model = model.PopulationModel('data/np2023.csv',agerange0)
ins_model = model.InsuranceModel('data/ACS ST 5Y 2023 Data.xlsx', ages0)
death_model = model.DeathRateModel('data/Mortality Data 2021-2022.csv',agesD0)

population = pop_model.get_population()
pci = ins_model.compute_insurance_ratio()
death_rate = death_model.compute_death_rate()

sim = model.HealthImpactSimulator(1.4, [1.06, 1.84], population, pci,death_rate)
### I need to make all the 19--55 age group calculations work for sim model too.

#  Scenarios of insurance loss for age-group 19--65
#atrisk = [20272000, 36188000]    # Expansion, Total
#atrisk = [0.796*i for i in atrisk]
#atrisk = [13300000, 23900000]
#atrisk = list(get_at_risk(age_upper_bound))
#automatic_exemption = [1-0.506221869,0] # 64
#automatic_exemption = [1-0.475364278,0] # 55
#reporting_rate = [0.18,0.28,0]

atrisk, reporting_rate, automatic_exemption = get_inputs(age_upper_bound)


descriptions = list(product(atrisk, automatic_exemption, reporting_rate))

## Morbidity inputs:
# Diabetes
def get_morbidity_input(age_upper_bound=55,disease='diabetes'):
    if disease == 'diabetes':
        prev55 = 0.048; prev65 = 0.189; # 4.8% for 18-44 approximating for 19-55, 18.9% among 55-64.
        # https://www.cdc.gov/diabetes/php/data-research/index.html
        pop55 = 158334581; pop65 = 199563303; # grabbed from data.
        uprev55 = 0.305; uprev65 = 0.298; # 30.5% uncontrolled prev. among 18-44 approx for 19-55 and 29.8% unc. prev. among 55-64
        # https://www.cdc.gov/diabetes/php/data-research/appendix.html (Appendix A: Table 9)
        eru = 1.99; # https://www.sciencedirect.com/science/article/pii/S0091743520302048
    elif disease == 'hypertension':
        prev55 = 0.329;  prev65 = 0.329;  # 4.8% for 18-44 approximating for 19-55, 18.9% among 55-64.
        uprev55 = 0.518; uprev65 = 0.518;  # https://www.ahajournals.org/doi/10.1161/HYPERTENSIONAHA.122.19222
        eru = 1/0.63 # https://academic.oup.com/ajh/article/20/4/348/141573
    else:
        prev55 = 0.329; prev65 = 0.329;

    if age_upper_bound == 55:
        dp = prev55
        ud = uprev55
    else:
        dp = (prev55*pop55 + prev65*(pop65-pop55))/pop65
        ud = (uprev55*prev55*pop55 + uprev65*prev65*(pop65-pop55))/(dp*pop65)
    return dp, ud, eru

dp, ud, eru = get_morbidity_input(age_upper_bound)

## Other references for morbidities
# Hypertension: https://pmc.ncbi.nlm.nih.gov/articles/PMC7803011/, https://www.cdc.gov/nchs/products/databriefs/db511.htm
#


results = pd.DataFrame(index=range(len(descriptions)),
                       columns=['at risk', 'ae', 'rr', 'pli','li','median','lci','uci'])


morbidity = pd.DataFrame(index=range(len(descriptions)),
                         columns = ['at risk', 'ae', 'rr', 'pli','li','current','updated','additional'])


for i in range(len(descriptions)):
    description = list(descriptions[i])
    pli = (1-description[1])*(1-description[2])
    li = pli*description[0]
    pui = sim.simulate_uninsurance(li)
    excess = sim.compute_excess_deaths(pui, True)
    results.iloc[i] = np.append(list(descriptions[i])+[pli,li], np.quantile(excess,[0.5,0.025,0.975]))
    morbidity.iloc[i] = np.append(list(descriptions[i]) + [pli, li], list(get_morbidity_results(population, dp, ud, pci['mode'], pui['mode'], eru)))


## To add results for additional uncontrolled diabetes and xxx, what do I need:
## I need current prevalence, prevalence among prevalence, and hazard ratio.
