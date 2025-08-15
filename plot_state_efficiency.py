
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load data
df_full = pd.read_csv("results/state_mortality_ci_Full_Exemption.csv").set_index("state")
df_limited = pd.read_csv("results/state_mortality_ci_Limited_Exemption.csv").set_index("state")
df_eff = pd.read_csv("results/state_mortality_ci_Efficiency_based_Exemption.csv").set_index("state")

# Merge all into one DataFrame
df = df_full[["median"]].rename(columns={"median": "full"})
df["limited"] = df_limited["median"]
df["eff"] = df_eff["median"]

# Calculate normalized value
df["normalized"] = (df["eff"] - df["full"]) / (df["limited"] - df["full"])
df = df.dropna().sort_values("normalized")

# Plot
plt.figure(figsize=(8, 16))
plt.hlines(y=df.index, xmin=0, xmax=1, color="lightgray", linewidth=1)
plt.plot(df["normalized"], df.index, "o", color="darkred")
plt.xlabel("Relative Mortality Position\n(0 = Full Exemption, 1 = Limited Exemption)")
plt.title("Normalized Efficiency-Based Mortality by State")
plt.xlim(0, 1)

# Save
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/figure_5_normalized_efficiency_position.png", dpi=300)
plt.close()
