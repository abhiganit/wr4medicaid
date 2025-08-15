import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure plots/ directory exists
os.makedirs("plots", exist_ok=True)

# Load data
df_ci = pd.read_csv("results/national_mortality_ci.csv")
df_grid = pd.read_csv("results/national_mortality_grid.csv")

# --- Start Plotting ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))


# Panel A: Bar chart with 95% CI and labels
labels = ["CBO-based", "Arkansas-based", "New Hampshire-based"]
bars = axes[0].bar(labels, df_ci['median'],
                   #yerr=[df_ci['median'] - df_ci['lci'], df_ci['uci'] - df_ci['median']],
                   capsize=5, color="steelblue", edgecolor="black")

axes[0].set_ylabel("Excess Deaths (Annual)",fontsize=12)
axes[0].set_xlabel("Scenario",fontsize=12)
axes[0].set_title("A. National Excess Mortality by Scenario")
axes[0].set_ylim(0, df_ci['median'].max() * 1.2)
axes[0].spines.right.set_visible(False)
axes[0].spines.top.set_visible(False)


# Add numbers on top of bars
for i, val in enumerate(df_ci['median']):
    axes[0].text(i, val + 0.01 * df_ci['uci'].max(), f"{round(val):,}", ha='center', va='bottom', fontsize=12)


# Panel B: P-color plot
# Panel B: Contour + labeled lines plot
pivot = df_grid.pivot(index="failure_to_report", columns="efficiency", values="median")
eff = pivot.columns.values
fail = pivot.index.values
Z = pivot.values

# Filled contour background
contour_filled = axes[1].contourf(eff, fail, Z, levels=15, cmap="viridis_r")
cbar = fig.colorbar(contour_filled, ax=axes[1])
cbar.set_label("Excess Deaths (Annual)")

# Add labeled contour lines
contour_lines = axes[1].contour(eff, fail, Z, levels=10, colors="black", linewidths=0.7)
axes[1].clabel(contour_lines, inline=True, fontsize=8, fmt="%.0f")

# Add Arkansas and New Hampshire markers
axes[1].plot(1, 0.72, 'ro', label='Arkansas-based Scenario')
axes[1].plot(1, 0.82, 's', color='orange', label='New Hampshire-based Scenario')
axes[1].text(0.78, 0.72, "Arkansas-based", va='center', ha='left', color='red', fontsize=9)
axes[1].text(0.69, 0.82, "New Hampshire-based", va='center', ha='left', color='orange', fontsize=9)

axes[1].set_xlabel("Auto-Exemption Efficiency",fontsize=12)
axes[1].set_ylabel("Non-compliance Rate",fontsize=12)
axes[1].set_title("B. Excess Mortality by Auto-Exemption and Reporting Compliance")
#axes[1].legend(loc="lower right", fontsize=8)


# pivot = df_grid.pivot(index="failure_to_report", columns="efficiency", values="median")
# eff = pivot.columns.values
# fail = pivot.index.values
# heatmap = axes[1].pcolormesh(eff, fail, pivot.values, shading="auto", cmap="viridis")
# cbar = fig.colorbar(heatmap, ax=axes[1])
# cbar.set_label("Estimated Excess Deaths")
#
# # Add scenario markers
# axes[1].plot(1, 0.72, marker='o', color='red', label='Arkansas Scenario')
# axes[1].plot(1, 0.82, marker='s', color='orange', label='New Hampshire Scenario')
# axes[1].text(1.02, 0.72, "Arkansas", va='center', ha='left', color='red', fontsize=9)
# axes[1].text(1.02, 0.82, "New Hampshire", va='center', ha='left', color='orange', fontsize=9)
#
# axes[1].set_xlabel("Exemption Efficiency")
# axes[1].set_ylabel("Failure to Report")
# axes[1].set_title("B. Mortality Grid of p (efficiency) and r (reporting)")
# axes[1].legend(loc='lower right', fontsize=8)


# Finalize and save
plt.tight_layout()
plt.savefig("plots/figure_1_national_mortality.pdf")
plt.savefig("plots/figure_1_national_mortality.png", dpi=300)
plt.close()
