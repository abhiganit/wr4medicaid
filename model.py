import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import scipy.stats as stats
from numpy.random import RandomState
from pandas.core.apply import is_multi_agg_with_relabel


def normal(value, ci, alp=0.975, sample_size=1000, seed=5):
    """
    Create a log-normal distribution approximation based on confidence interval.
    """
    mean = np.log(value)
    std = (np.log(ci[1]) - np.log(ci[0])) / (2 * stats.norm.ppf(alp))
    dist = stats.norm(loc=mean, scale=std)
    dist.mode = np.exp(mean)
    rng = RandomState(seed)
    dist.sample = np.exp(rng.normal(mean, std, sample_size))
    return dist

# Note: make it age-group dependent.
class PopulationModel:
    def __init__(self, filepath,ages):
        self.data = pd.read_csv(filepath)
        self.ages = ages

    # age_row must not be 9 default value should be 3 (for now keeping this)
    # start_col = 4+ age0 and end_col = 4+age1
    def get_population(self, sex=0, origin=0, race=0, year_row=3, zero_col=4):
        pop_subset = self.data[
            (self.data['SEX'] == sex) &
            (self.data['ORIGIN'] == origin) &
            (self.data['RACE'] == race)
        ]
        start_col = zero_col+self.ages[0]
        end_col = zero_col+self.ages[-1]
        return pop_subset.iloc[year_row, start_col:end_col].sum()

# this already works for both age groups of interest
class InsuranceModel:
    def __init__(self, filepath, ages, location='United States', sheet='Data'):
        self.raw_data = pd.read_excel(filepath, sheet_name=sheet, header=[0, 1, 2], index_col=0)
        self.ages = ages
        self.location = location
        self.cleaned_data = self._clean_data()

    def _clean_data(self):
        df = self.raw_data.copy()
        df.loc[self.ages] = df.loc[self.ages].replace({',': '', '±': ''}, regex=True)
        df.loc[self.ages] = df.loc[self.ages].apply(pd.to_numeric, errors='coerce')
        return df

    def compute_insurance_ratio(self):
        data = self.cleaned_data.loc[self.ages].sum()
        location = self.location
        insured = data[(location,'Insured','Estimate')]
        total = data[(location,'Total','Estimate')]
        insured_margin = data[(location,'Insured','Margin of Error')]
        total_margin = data[(location,'Total','Margin of Error')]
        return self._get_ins(total, insured, total_margin, insured_margin)

    def _get_ins(self, p, i, pm, im):
        """
        Estimate the ratio of insured/total with uncertainty.
        """
        pD = normal(p, [p - pm, p + pm], 0.95)
        pI = normal(i, [i - im, i + im], 0.95)
        return {
            'mode': pI.mode / pD.mode,
            'sample': pI.sample / pD.sample
        }

# this will also be age dependent
# Just use a different way to slice things and add age
class DeathRateModel:
    def __init__(self, filepath,ages):
        self.data = pd.read_csv(filepath)
        self.ages = ages

    def compute_death_rate(self):
        df_ = self.data.copy()
        df = df_[df_['Age_Group_Years'].isin(self.ages)]
        deaths = df['2022_Number'].sum()
        pop = 100000 * (df['2022_Number'] / df['2022_Rate_per_100000']).sum()
        return deaths / pop

# how is this being calculated?
# death rate should become part of self.
class HealthImpactSimulator:
    def __init__(self, hazard_ratio_value, hazard_ratio_ci, population, insurance_ratio, death_rate):
        self.population = population
        self.pci = insurance_ratio
        self.hazard = normal(hazard_ratio_value, hazard_ratio_ci)
        self.death_rate = death_rate

    def simulate_uninsurance(self, uninsured_lost):
        return {
            'mode': max(0, self.pci['mode'] - uninsured_lost / self.population),
            'sample': self.pci['sample'] - uninsured_lost / self.population
        }

    def compute_excess_deaths(self, pui, simulate=False):
        if simulate:
            return self._simulate_excess_deaths(self.population, self.death_rate, self.pci['sample'], pui['sample'],
                                                self.hazard.sample)
        else:
            return self._excess_deaths(self.population, self.death_rate, self.pci['mode'], pui['mode'], self.hazard.mode)[2]

    def _simulate_excess_deaths(self, Pa, dr, pcai_samples, puai_samples, hr_samples):
        """
        Monte Carlo simulation of excess deaths using samples.
        """
        Da = dr * Pa
        scaling_factors = (puai_samples + hr_samples * (1 - puai_samples)) / (
                    pcai_samples + hr_samples * (1 - pcai_samples))
        Du_samples = scaling_factors * Da
        Dx_samples = Du_samples - Da
        return Dx_samples

    def _scaling_factor(self, pcai, puai, hr):
        return (puai + hr * (1 - puai)) / (pcai + hr * (1 - pcai))

    def _excess_deaths(self, Pa, dr, pcai, puai, hr):
        """
        Compute baseline deaths, updated deaths, and excess deaths.
        """
        Da = dr * Pa
        Du = self._scaling_factor(pcai, puai, hr) * Da
        return Da, Du, Du - Da





