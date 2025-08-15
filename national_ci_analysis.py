
import pandas as pd
import numpy as np
from simulation_utils import SimulationConfig, NationalSimulator
from model import MorbidityCalculator, HealthImpactSimulator
import model

def summarize(samples):
    return {
        'median': np.median(samples),
        'lci': np.quantile(samples, 0.025),
        'uci': np.quantile(samples, 0.975)
    }

def run_national_mortality_and_morbidity(loss_values,other = False):
    config = SimulationConfig(age_upper_bound=64)
    national_sim = NationalSimulator(config)
    results_df = []
    morbidity_df = []

    for loss in loss_values:
        population = national_sim.population_model.get_population()
        pci = national_sim.ins_model.compute_insurance_ratio()
        death_rate = national_sim.death_model.compute_death_rate()
        if other == True:
            sim = HealthImpactSimulator(1.27, [1.27, 1.27], population, pci, death_rate)
        else:
            sim = national_sim.get_simulator()
        pui = sim.simulate_uninsurance(loss)
        excess = sim.compute_excess_deaths(pui, simulate=True)
        summary = summarize(excess)
        summary.update({'insurance_loss': loss})
        results_df.append(summary)

        for disease in ['diabetes', 'hypertension', 'cholesterol']:
            calc = MorbidityCalculator(disease, config)
            morb_summary = calc.simulate_ci(pci, pui, population)
            morb_summary.update({'insurance_loss': loss, 'disease': disease})
            morbidity_df.append(morb_summary)

    df_mortality = pd.DataFrame(results_df)
    df_morbidity = pd.DataFrame(morbidity_df)

    return df_mortality, df_morbidity

def run_national_grid_scenario(eff_range=np.linspace(0, 1, 101), report_range=np.linspace(0.5, 0.9, 41)):
    xls = pd.ExcelFile('data/state-level-coverage-loss.xlsx')
    df = xls.parse("Data").dropna().iloc[0:]

    # Use first row ('total') for national loss base
    loss_L = df.iloc[0, 11]  # Column L
    loss_M = df.iloc[0, 12]  # Column M

    config = SimulationConfig(age_upper_bound=64)
    national_sim = NationalSimulator(config)
    population = national_sim.population_model.get_population()
    pci = national_sim.ins_model.compute_insurance_ratio()
    death_rate = national_sim.death_model.compute_death_rate()

    results = []
    for p in eff_range:
        for r in report_range:
            loss = r * (p * loss_L + (1 - p) * loss_M)
            sim = HealthImpactSimulator(1.4, [1.06, 1.84], population, pci, death_rate)
            pui = sim.simulate_uninsurance(loss)
            excess = sim.compute_excess_deaths(pui, simulate=True)
            summary = summarize(excess)
            summary.update({
                'efficiency': p,
                'failure_to_report': r,
                'insurance_loss': loss
            })
            results.append(summary)

    df = pd.DataFrame(results)
    df.to_csv("results/national_mortality_grid.csv", index=False)
    print("Saved national_mortality_grid.csv")


if __name__ == "__main__":
    # Run standard scenarios
    insurance_losses = [4_800_000, 5_500_000, 6_300_000]
    df_mortality, df_morbidity = run_national_mortality_and_morbidity(insurance_losses)
    df_mortality.to_csv("results/national_mortality_ci.csv", index=False)
    df_morbidity.to_csv("results/national_morbidity_ci.csv", index=False)
    print("Saved standard national results.")

    df_mortality_other, df_morbidity_other = run_national_mortality_and_morbidity(insurance_losses,True)
    df_mortality_other.to_csv("results/national_mortality_ci_hr127.csv", index=False)
    df_morbidity_other.to_csv("results/national_morbidity_ci_hr127.csv", index=False)
    print("Saved other national results.")
    # Uncomment below to run grid
    run_national_grid_scenario()
