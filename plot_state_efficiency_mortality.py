import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.colors import PowerNorm, Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.gridspec import GridSpec

# Load shapefile
gdf = gpd.read_file("shapefile/tl_2017_us_state.shp").to_crs(epsg=2163)
gdf = gdf.rename(columns={"NAME": "state"})
gdf.loc[gdf.state == "Alaska", "geometry"] = gdf.loc[gdf.state == "Alaska"].scale(0.2, 0.2, 0.2).translate(1.4e6, -4.5e6)
gdf.loc[gdf.state == "Hawaii", "geometry"] = gdf.loc[gdf.state == "Hawaii"].scale(0.8, 0.8, 0.8).translate(5e6, -1.35e6)

# Load mortality data
df_eff = pd.read_csv("results/state_mortality_ci_Efficiency_based_Exemption.csv").set_index("state")
df_full = pd.read_csv("results/state_mortality_ci_Full_Exemption.csv").set_index("state")
df_limited = pd.read_csv("results/state_mortality_ci_Limited_Exemption.csv").set_index("state")

# Merge and compute normalized position
df = df_eff[["median", "per_capita_median"]].rename(columns={"median": "eff", "per_capita_median": "eff_pc"})
df["full"] = df_full["median"]
df["limited"] = df_limited["median"]
df["normalized"] = (df["limited"] - df["eff"]) / (df["limited"] - df["full"])
df = df.dropna()

# Normalize color scale for absolute excess deaths
norm = PowerNorm(gamma=0.5, vmin=df["eff"].min(), vmax=df["eff"].max())
cmap = plt.cm.Reds
df["color"] = [cmap(norm(val)) for val in df["eff"]]

# Sort for lollipop plot
df_sorted = df.sort_values("normalized")

# Set up custom 2x2 layout with GridSpec
fig = plt.figure(figsize=(16, 12), constrained_layout=True)
gs = GridSpec(2, 2, figure=fig)
ax_map_abs = fig.add_subplot(gs[0, 0])
ax_map_pc = fig.add_subplot(gs[1, 0])
ax_lollipop = fig.add_subplot(gs[:, 1])

# Map A: Absolute deaths
merged = gdf.merge(df, on="state", how="left")
merged.plot(column="eff", cmap="Reds", linewidth=0.8, ax=ax_map_abs, edgecolor="0.8",
            legend=False, norm=norm, missing_kwds={"color": "lightgray", "label": "No Data"})
ax_map_abs.set_xlim(-2e6, 2.5e6)
ax_map_abs.set_ylim(-2.4e6, 0.8e6)
ax_map_abs.set_title("A. Excess Deaths: Efficiency-based Exemption", fontsize=14)
ax_map_abs.axis("off")

cax1 = inset_axes(ax_map_abs, width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0.0, 0.04, 1, 1), bbox_transform=ax_map_abs.transAxes, borderpad=0)
sm1 = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm1._A = []
cbar1 = fig.colorbar(sm1, cax=cax1, orientation="horizontal")
cbar1.set_label("Annual Excess Deaths", fontsize=12)
tick_vals = [0, 100, 250, 500, 1000, 1500, 2000]
cbar1.set_ticks([0, 250, 500, 1000, 2000])
cbar1.set_ticklabels(["0", "250", "500", "1,000", "2,000"])

# Map B: Per capita deaths
norm_pc = Normalize(vmin=df["eff_pc"].min(), vmax=df["eff_pc"].max())
merged.plot(column="eff_pc", cmap="YlOrRd", linewidth=0.8, ax=ax_map_pc, edgecolor="0.8",
            legend=False, norm=norm_pc, missing_kwds={"color": "lightgray", "label": "No Data"})
ax_map_pc.set_xlim(-2e6, 2.5e6)
ax_map_pc.set_ylim(-2.4e6, 0.8e6)
ax_map_pc.set_title("B. Excess Deaths per 100,000", fontsize=14)
ax_map_pc.axis("off")

cax2 = inset_axes(ax_map_pc, width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0.0, -0.05, 1, 1), bbox_transform=ax_map_pc.transAxes, borderpad=0)
sm2 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=norm_pc)
sm2._A = []
cbar2 = fig.colorbar(sm2, cax=cax2, orientation="horizontal")
cbar2.set_label("Excess Deaths per 100,000", fontsize=12)

# Lollipop Plot: States on y-axis, relative position on x-axis
ax_lollipop.hlines(y=df_sorted.index, xmin=0, xmax=1, color="lightgray", linestyles="dashed", linewidth=1)
ax_lollipop.scatter(df_sorted["normalized"], df_sorted.index, color=df_sorted["color"], edgecolor="black", s=60, zorder=3)
ax_lollipop.set_xlim(0, 1)
ax_lollipop.set_xticks([0, 0.5, 1])
ax_lollipop.set_xlabel("Proportion of Preventable Mortality Averted",fontsize=14)
ax_lollipop.set_title("C. Proportion of Preventable Mortality Averted through Auto-Exemption Efficiency", fontsize=14)
for label in ax_lollipop.get_yticklabels():
    label.set_fontweight('bold')
    label.set_fontsize(10)

# Save
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/figure_3_map_and_lollipop_2x2.png", dpi=300, bbox_inches="tight")
plt.savefig("plots/figure_3_map_and_lollipop_2x2.pdf")
plt.close()
