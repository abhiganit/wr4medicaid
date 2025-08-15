
import pandas as pd
import numpy as np
import os
from simulation_utils import SimulationConfig, StateSimulator
from model import MorbidityCalculator

def summarize(samples):
    return {
        'median': np.median(samples),
        'lci': np.quantile(samples, 0.025),
        'uci': np.quantile(samples, 0.975)
    }

def run_state_scenario(scenario='Full_Exemption'):
    pop_df = pd.read_excel('data/state_pop.xlsx', index_col=0).drop(index='Puerto Rico')
    loss_df = pd.read_excel('data/state-level-coverage-loss.xlsx', sheet_name='Data', usecols="A,N:O")
    loss_df.columns = ['state', 'Full_Exemption', 'Limited_Exemption']
    loss_df = loss_df.dropna().iloc[1:]
    loss_df.set_index('state', inplace=True)

    ex_df = None
    if scenario == 'Efficiency_based_Exemption':
        ex_df = pd.read_csv('data/ex_parte_rates.csv')
        ex_df.set_index('state', inplace=True)

    config = SimulationConfig(age_upper_bound=64)
    simulator = StateSimulator(config, pop_df)

    all_mortality = []
    all_morbidity = []

    for state in pop_df.index:
        if state not in loss_df.index or (scenario == 'Efficiency_based_Exemption' and state not in ex_df.index):
            print(f"Skipping {state} (missing data)")
            continue

        if scenario == 'Efficiency_based_Exemption':
            loss_full = loss_df.loc[state, 'Full_Exemption']
            loss_limited = loss_df.loc[state, 'Limited_Exemption']
            efficiency = ex_df.loc[state, 'ex_parte_rate']
            loss = (1-efficiency) * loss_limited + efficiency * loss_full
        else:
            loss = loss_df.loc[state, scenario]

        pop = pop_df.loc[state, 'Prop:19-64'] * simulator.total_population
        pui = simulator.simulate_uninsurance_for_state(state, loss)
        excess = simulator.sim.compute_excess_deaths(pui, simulate=True)
        pci = simulator.sim.pci

        m = summarize(excess)
        per_100k = 100000 / pop
        m.update({
            'insurance_loss': loss,
            'state': state,
            'scenario': scenario,
            'per_capita_median': m['median'] * per_100k,
            'per_capita_lci': m['lci'] * per_100k,
            'per_capita_uci': m['uci'] * per_100k
        })
        all_mortality.append(m)

        for disease in ['diabetes', 'hypertension', 'cholesterol']:
            calc = MorbidityCalculator(disease, config)
            b = calc.simulate_ci(pci, pui, pop)
            b.update({'insurance_loss': loss, 'state': state, 'scenario': scenario, 'disease': disease})
            all_morbidity.append(b)

    pd.DataFrame(all_mortality).to_csv(f"results/state_mortality_ci_{scenario}.csv", index=False)
    pd.DataFrame(all_morbidity).to_csv(f"results/state_morbidity_ci_{scenario}.csv", index=False)
    print(f"Saved results for scenario: {scenario}")

def run_state_grid_scenario(eff_range=np.linspace(0, 1, 11), report_range=np.linspace(0.5, 0.9, 5)):
    pop_df = pd.read_excel('data/state_pop.xlsx', index_col=0).drop(index='Puerto Rico')
    loss_df = pd.read_excel('data/state-level-coverage-loss.xlsx', sheet_name='Data')
    loss_df = loss_df.dropna().iloc[1:]
    loss_df.set_index(loss_df.columns[0], inplace=True)
    Eligible_No_Exemptions = loss_df.iloc[:, 11]
    Eligible_Parents_Only = loss_df.iloc[:, 12]

    config = SimulationConfig(age_upper_bound=64)
    simulator = StateSimulator(config, pop_df)

    for state in pop_df.index:
        if state not in loss_df.index:
            continue

        loss_L = Eligible_No_Exemptions.loc[state]
        loss_M = Eligible_Parents_Only.loc[state]
        pop = pop_df.loc[state, 'Prop:19-64'] * simulator.total_population

        results = []
        for p in eff_range:
            for r in report_range:
                est_loss = r * (p * loss_L + (1 - p) * loss_M)
                pui = simulator.simulate_uninsurance_for_state(state, est_loss)
                excess = simulator.sim.compute_excess_deaths(pui, simulate=True)
                pci = simulator.sim.pci

                m = summarize(excess)
                per_100k = 100000 / pop
                m.update({
                    'efficiency': p,
                    'failure_to_report': r,
                    'state': state,
                    'estimated_loss': est_loss,
                    'per_capita_median': m['median'] * per_100k,
                    'per_capita_lci': m['lci'] * per_100k,
                    'per_capita_uci': m['uci'] * per_100k
                })
                results.append(m)

        outdir = f"results/{state.replace(' ', '_')}"
        os.makedirs(outdir, exist_ok=True)
        pd.DataFrame(results).to_csv(f"{outdir}/mortality_grid.csv", index=False)

    print("Saved grid-based results to results/<state>/mortality_grid.csv")

if __name__ == "__main__":
    run_state_scenario("Efficiency_based_Exemption")
    #run_state_grid_scenario()  # Uncomment to run grid
