
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import scipy.stats as stats
from numpy.random import RandomState

def normal(value, ci, alp=0.975, sample_size=1000, seed=5):
    mean = np.log(value)
    std = (np.log(ci[1]) - np.log(ci[0])) / (2 * stats.norm.ppf(alp))
    dist = stats.norm(loc=mean, scale=std)
    dist.mode = np.exp(mean)
    rng = RandomState(seed)
    dist.sample = np.exp(rng.normal(mean, std, sample_size))
    return dist

class PopulationModel:
    def __init__(self, filepath, ages):
        self.data = pd.read_csv(filepath)
        self.ages = ages

    def get_population(self, sex=0, origin=0, race=0, year_row=3, zero_col=4):
        pop_subset = self.data[
            (self.data['SEX'] == sex) &
            (self.data['ORIGIN'] == origin) &
            (self.data['RACE'] == race)
        ]
        start_col = zero_col + self.ages[0]
        end_col = zero_col + self.ages[-1]
        return pop_subset.iloc[year_row, start_col:end_col].sum()

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
        insured = data[(location, 'Insured', 'Estimate')]
        total = data[(location, 'Total', 'Estimate')]
        insured_margin = data[(location, 'Insured', 'Margin of Error')]
        total_margin = data[(location, 'Total', 'Margin of Error')]
        return self._get_ins(total, insured, total_margin, insured_margin)

    def _get_ins(self, p, i, pm, im):
        pD = normal(p, [p - pm, p + pm], 0.95)
        pI = normal(i, [i - im, i + im], 0.95)
        return {
            'mode': pI.mode / pD.mode,
            'sample': pI.sample / pD.sample
        }

class DeathRateModel:
    def __init__(self, filepath, ages):
        self.data = pd.read_csv(filepath)
        self.ages = ages

    def compute_death_rate(self):
        df_ = self.data.copy()
        df = df_[df_['Age_Group_Years'].isin(self.ages)]
        deaths = df['2022_Number'].sum()
        pop = 100000 * (df['2022_Number'] / df['2022_Rate_per_100000']).sum()
        return deaths / pop

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
            return self._simulate_excess_deaths(self.population, self.death_rate, self.pci['sample'], pui['sample'], self.hazard.sample)
        else:
            return self._excess_deaths(self.population, self.death_rate, self.pci['mode'], pui['mode'], self.hazard.mode)[2]

    def _simulate_excess_deaths(self, Pa, dr, pcai_samples, puai_samples, hr_samples):
        Da = dr * Pa
        scaling_factors = (puai_samples + hr_samples * (1 - puai_samples)) / (pcai_samples + hr_samples * (1 - pcai_samples))
        Du_samples = scaling_factors * Da
        Dx_samples = Du_samples - Da
        return Dx_samples

    def _scaling_factor(self, pcai, puai, hr):
        return (puai + hr * (1 - puai)) / (pcai + hr * (1 - pcai))

    def _excess_deaths(self, Pa, dr, pcai, puai, hr):
        Da = dr * Pa
        Du = self._scaling_factor(pcai, puai, hr) * Da
        return Da, Du, Du - Da

class MorbidityCalculator:
    def __init__(self, disease, config):
        self.disease = disease.lower()
        self.config = config

    def get_inputs(self):
        pop55 = 158334581;
        pop65 = 199563303
        if self.config.age_upper_bound == 55:
            pop = 158334581
        else:
            pop = 199563303
        if self.disease == 'diabetes':
            prev55, prev65 = 0.048, 0.189
            uprev55, uprev65 = 0.305, 0.298
            eru = 1.855
            if self.config.age_upper_bound == 55:
                dp = prev55
                ud = uprev55
            elif self.config.age_upper_bound == 64:
                dp = (prev55 * pop55 + prev65 * (pop65 - pop55)) / pop65
                ud = (uprev55 * prev55 * pop55 + uprev65 * prev65 * (pop65 - pop55)) / (dp * pop65)
            else:
                raise ValueError("Unsupported age upper bound (only 55 or 64 supported)")
            return pop, dp, ud, eru

        elif self.disease == 'hypertension':
            eru = 0.055
            if self.config.age_upper_bound == 55:
                dp = 0.35
                ud = 0.9
            elif self.config.age_upper_bound == 64:
                dp = 0.39
                ud = 0.92
            else:
                raise ValueError("Unsupported age upper bound (only 55 or 64 supported)")
            return pop, dp, ud, eru
        elif self.disease == 'cholesterol':
            eru = 0.050
            if self.config.age_upper_bound == 55:
                dp = 0.10
                ud = 0.55
            elif self.config.age_upper_bound == 64:
                dp = 0.12
                ud = 0.63
            else:
                raise ValueError("Unsupported age upper bound (only 55 or 64 supported)")
            return pop, dp, ud, eru
        elif self.disease == 'asthma':
            eru = 1.1
            if self.config.age_upper_bound == 55:
                dp = 0.087
                ud = 0.404
            elif self.config.age_upper_bound == 64:
                dp = 0.087
                ud = 0.404
            else:
                raise ValueError("Unsupported age upper bound (only 55 or 64 supported)")
            return pop, dp, ud, eru
        elif self.disease == 'depression':
            eru = 1.18
            if self.config.age_upper_bound == 55:
                dp = 0.228
                ud = 0.461
            elif self.config.age_upper_bound == 64:
                dp = 0.228
                ud = 0.461
            else:
                raise ValueError("Unsupported age upper bound (only 55 or 64 supported)")
            return pop, dp, ud, eru
        elif self.disease == 'substance_use':
            eru = 1.075
            if self.config.age_upper_bound == 55:
                dp = 0.171
                ud = 0.764
            elif self.config.age_upper_bound == 64:
                dp = 0.171
                ud = 0.764
            return pop, dp, ud, eru
        else:
            raise ValueError("Unsupported disease type")

    def simulate_ci(self, pci, pui, population, n_samples=1000):
        pop, dp, ud, eru = self.get_inputs()
        current_uncontrolled = ud * dp * population
        samples = []

        use_relative_risk = self.disease == 'diabetes'
        for i in range(n_samples):
            cur_cov =pci['sample'][i]
            upd_cov = pui['sample'][i]
            if use_relative_risk:
                multiplier = (upd_cov + eru * (1 - upd_cov)) / (cur_cov + eru * (1 - cur_cov))
                projected_uncontrolled = multiplier * current_uncontrolled
            else:
                delta_coverage = cur_cov - upd_cov
                excess_uncontrolled = population * dp * delta_coverage * eru
                projected_uncontrolled = current_uncontrolled + excess_uncontrolled
            samples.append(projected_uncontrolled - current_uncontrolled)

        return {
            'median': np.median(samples),
            'lci': np.quantile(samples, 0.025),
            'uci': np.quantile(samples, 0.975),
            'current_uncontrolled': current_uncontrolled
        }
