
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.colors import PowerNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Load shapefile
gdf = gpd.read_file("shapefile/tl_2017_us_state.shp").to_crs(epsg=2163)
gdf = gdf.rename(columns={"NAME": "state"})

# Reposition Alaska and Hawaii
gdf.loc[gdf.state == "Alaska", "geometry"] = gdf.loc[gdf.state == "Alaska"].scale(0.2, 0.2, 0.2).translate(1.4e6, -4.5e6)
gdf.loc[gdf.state == "Hawaii", "geometry"] = gdf.loc[gdf.state == "Hawaii"].scale(0.8, 0.8, 0.8).translate(5e6, -1.35e6)

# Scenario data files
scenarios = {
    "Full Exemption": "results/state_mortality_ci_Full_Exemption.csv",
    "Efficiency-based Exemption": "results/state_mortality_ci_Efficiency_based_Exemption.csv",
    "Limited Exemption": "results/state_mortality_ci_Limited_Exemption.csv"
}

# Output folder
os.makedirs("plots", exist_ok=True)

# Calculate vmin/vmax across all files
all_data = []
for path in scenarios.values():
    df = pd.read_csv(path)
    all_data.extend(df["per_capita_median"].dropna().values)
vmin, vmax = min(all_data), max(all_data)

# Set up nonlinear normalization
norm = PowerNorm(gamma=0.5, vmin=vmin, vmax=vmax)

# Set up figure
fig, axes = plt.subplots(1, 3, figsize=(16, 6), constrained_layout=False)
plt.subplots_adjust(wspace=0.05)

# Plot maps
for ax, (label, path) in zip(axes, scenarios.items()):
    df = pd.read_csv(path)
    merged = gdf.merge(df, on="state", how="left")
    merged.plot(
        column="per_capita_median",
        cmap="Oranges",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        norm=norm,
        legend=False,
        missing_kwds={"color": "lightgray", "label": "No Data"},
    )
    ax.set_xlim(-2e6, 2.5e6)
    ax.set_ylim(-2.4e6, 0.8e6)
    ax.set_title(label, fontsize=14)
    ax.axis("off")

# Shared colorbar below panels
cax = inset_axes(
    axes[1],
    width="150%", height="8%",
    loc="lower center",
    bbox_to_anchor=(0, -0.1, 1, 1),
    bbox_transform=axes[1].transAxes,
    borderpad=0
)
sm = plt.cm.ScalarMappable(cmap="Oranges", norm=norm)
sm._A = []
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
cbar.set_label("Excess Deaths per 100,000", fontsize=14)
cbar.ax.tick_params(labelsize=12)

# Save figure
plt.savefig("plots/figure_4_state_per_capita_mortality_map.png", dpi=300)
plt.close()
