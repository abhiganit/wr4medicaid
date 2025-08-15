import pandas as pd
import matplotlib.pyplot as plt
import os

# Ensure output folder exists
os.makedirs("plots", exist_ok=True)

# Load the results (adjust path if needed)
df = pd.read_csv("results/national_morbidity_ci.csv")

# Label the scenarios
scenario_labels = {
    4800000: "CBO-based",
    5500000: "Arkansas-based",
    6300000: "New Hampshire-based"
}
df["scenario"] = df["insurance_loss"].map(scenario_labels)

# Pivot for bar plot
plot_df = df.pivot(index="scenario", columns="disease", values="median").reindex(["CBO-based", "Arkansas-based", "New Hampshire-based"])

# Plot
plt.figure(figsize=(10, 6))
plot_df.plot(kind="bar", ax=plt.gca(), width=0.75, color=["#66c2a5", "#fc8d62", "#8da0cb"])
plt.ylabel("Excess Uncontrolled Cases",fontsize=14)
plt.xlabel("Scenario",fontsize=14)
plt.title("Figure 2. National Excess Morbidity by Scenario")
plt.xticks(rotation=0)
plt.legend(['High Cholesterol','Diabetes','Hypertension'],title="Disease")

# Get the current axes object
ax = plt.gca()

# Remove the right and top spines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Add labels
for i, scenario in enumerate(plot_df.index):
    for j, disease in enumerate(plot_df.columns):
        value = plot_df.loc[scenario, disease]
        plt.text(i + j * 0.25 - 0.25, value + 0.01 * value, f"{round(value):,}", ha="center", fontsize=8)

# Save figure
plt.tight_layout()
plt.savefig("plots/figure_2_national_morbidity.png", dpi=300)
plt.savefig("plots/figure_2_national_morbidity.pdf")
plt.close()
