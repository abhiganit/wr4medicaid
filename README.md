# wr4medicaid
## Quantifying the Mortality and Morbidity Impact of Medicaid Work Requirements: A Modeling Study

**[Abhishek Pandey](mailto:abhishek.pandey@yale.edu), Yang Ye, Carolyn Bawden, Burton H. Singer, Alison P. Galvani, [The Center for Infectious Disease Modeling and Analysis](https://ysph.yale.edu/cidma/).**

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE. See [`LICENSE`](./LICENSE) for details.

This repository contains simulation and visualization code for 
quantifying the mortality and morbidity impacts of Medicaid work 
requirements in the United States. The analysis explores the 
consequences of insurance loss under various exemption and 
compliance scenarios using population data, disease control 
rates, and hazard ratios.


---

## Overview

- **Mortality Estimation**: Based on empirical hazard ratios and estimated insurance losses
- **Morbidity Projection**: Estimates additional uncontrolled cases of diabetes, hypertension, and high cholesterol
- **Scenario Analysis**: Varies automatic exemption efficiency and non-compliance to simulate realistic administrative outcomes
- **Visualizations**: Generates national and state-level plots, including p-color grid maps

---

##  Structure

| Folder / File                            | Description                                              |
|------------------------------------------|----------------------------------------------------------|
| `model.py`                               | Core classes for population, insurance, death modeling   |
| `simulation_utils.py`                   | High-level simulation wrappers (national & state)        |
| `national_ci_analysis.py`               | Runs national mortality and morbidity scenarios          |
| `state_ci_analysis.py`                  | Runs state-level simulations under 3 scenarios           |
| `data/`                                  | Input data files including coverage loss, rates          |
| `results/`                               | Saved outputs (CSV files)                                |
| `plots/`                                 | Generated figures                                        |

---

## Plotting Scripts

| Script                                     | Purpose                                                  |
|--------------------------------------------|-----------------------------------------------------------|
| `plot_national_mortality.py`              | Plots national mortality scenarios (bar + contour)        |
| `plot_national_morbidity.py`              | Plots national morbidity estimates                        |
| `plot_state_level_mortality.py`           | Maps state-level mortality estimates                      |
| `plot_state_level_per_capita_mortality.py`| Maps per capita state-level mortality                     |
| `plot_state_level_combined_mortality.py`  | Combines absolute and per capita mortality maps           |
| `plot_state_efficiency.py`                | Visualizes mortality differences due to efficiency gaps   |
| `plot_efficiency_vs_full.py`              | Plots deaths averted from full exemption vs. efficiency   |
| `plot_state_efficiency_mortality.py`      | Combined state-level maps + lollipop of normalized death  |
| `plot_state_grid_pages.py`                | Multi-panel p-color plots for state-level sensitivity (SI)|

---

## Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/wr4medicaid.git
   cd wr4medicaid
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the national analysis:
   ```bash
   python national_ci_analysis.py
   ```

4. Generate plots:
   ```bash
   python plot_national_mortality.py
   python plot_state_grid_pages.py
   ```

---

##  Supplementary Outputs

- Figures S1–S7 include state-level p-color plots illustrating the sensitivity of mortality estimates to administrative assumptions.
- Files are located in: `plots/pcolor_supplement/`

---




