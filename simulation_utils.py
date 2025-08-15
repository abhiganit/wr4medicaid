import pandas as pd
import numpy as np
import model


class SimulationConfig:
    def __init__(self, age_upper_bound=64, state=None):
        self.age_upper_bound = age_upper_bound
        self.state = state
        self.agerange, self.ages, self.agesD = self._get_age_inputs()

    def _get_age_inputs(self):
        if self.age_upper_bound == 55:
            return [19, 55], [
                '19 to 25 years', '26 to 34 years', '35 to 44 years', '45 to 54 years'
            ], ['15-24', '25-34', '35-44', '45-54']
        else:
            return [19, 65], [
                '19 to 25 years', '26 to 34 years', '35 to 44 years',
                '45 to 54 years', '55 to 64 years'
            ], ['15-24', '25-34', '35-44', '45-54', '55-64']

class StateSimulator:
    def __init__(self, config: SimulationConfig, df_state_pop):
        self.config = config
        self.df = df_state_pop
        self.population_model = model.PopulationModel('data/np2023.csv', self.config.agerange)
        self.death_model = model.DeathRateModel('data/Mortality Data 2021-2022.csv', self.config.agesD)
        self.total_population = self.population_model.get_population()

    def simulate_uninsurance_for_state(self, state, insurance_loss):
        if self.config.age_upper_bound == 55:
            pop_prop = self.df.loc[state, 'Prop:19-55']
        else:
            pop_prop = self.df.loc[state, 'Prop:19-64']

        pop = pop_prop * self.total_population

        ins_model = model.InsuranceModel('data/S2701 Selected Characteristics 2023.xlsx', self.config.ages, state)
        pci = ins_model.compute_insurance_ratio()
        death_rate = self.death_model.compute_death_rate()

        self.sim = model.HealthImpactSimulator(1.4, [1.06, 1.84], pop, pci, death_rate)
        pui = self.sim.simulate_uninsurance(insurance_loss)
        return pui

    def aggregate_across_states(self, all_results):
        # Assumes all states ran same number of scenarios in same order
        scenarios = list(all_results.values())[0][['insurance_loss']]
        combined = pd.DataFrame(index=range(len(scenarios)),
                                columns=scenarios.columns.tolist() + ['total_median', 'total_lci', 'total_uci'])

        for i in range(len(scenarios)):
            combined.iloc[i]['insurance_loss'] = scenarios.iloc[i]['insurance_loss']
            medians = [df.iloc[i]['median'] for df in all_results.values()]
            lciss = [df.iloc[i]['lci'] for df in all_results.values()]
            uciss = [df.iloc[i]['uci'] for df in all_results.values()]
            combined.iloc[i]['total_median'] = sum(medians)
            combined.iloc[i]['total_lci'] = sum(lciss)
            combined.iloc[i]['total_uci'] = sum(uciss)

        return combined

class NationalSimulator:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.population_model = model.PopulationModel('data/np2023.csv', config.agerange)
        self.ins_model = model.InsuranceModel('data/ACS ST 5Y 2023 Data.xlsx', config.ages)
        self.death_model = model.DeathRateModel('data/Mortality Data 2021-2022.csv', config.agesD)

    def get_simulator(self):
        population = self.population_model.get_population()
        pci = self.ins_model.compute_insurance_ratio()
        death_rate = self.death_model.compute_death_rate()
        return model.HealthImpactSimulator(1.4, [1.06, 1.84], population, pci, death_rate)
