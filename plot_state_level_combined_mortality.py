
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.colors import PowerNorm, Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Scenario to plot
scenario = "Full_Exemption"

# Load shapefile
gdf = gpd.read_file("shapefile/tl_2017_us_state.shp").to_crs(epsg=2163)
gdf = gdf.rename(columns={"NAME": "state"})
gdf.loc[gdf.state == "Alaska", "geometry"] = gdf.loc[gdf.state == "Alaska"].scale(0.2, 0.2, 0.2).translate(1.4e6, -4.5e6)
gdf.loc[gdf.state == "Hawaii", "geometry"] = gdf.loc[gdf.state == "Hawaii"].scale(0.8, 0.8, 0.8).translate(5e6, -1.35e6)

# Load data
df = pd.read_csv(f"results/state_mortality_ci_{scenario}.csv")
merged = gdf.merge(df, on="state", how="left")

# Output folder
os.makedirs("plots", exist_ok=True)

# Set up figure
fig, axes = plt.subplots(2, 1, figsize=(10, 12), constrained_layout=False)
plt.subplots_adjust(hspace=0.25)

# Panel A: Actual deaths
vmin1, vmax1 = merged["median"].min(), merged["median"].max()
norm1 = PowerNorm(gamma=0.5, vmin=vmin1, vmax=vmax1)
merged.plot(column="median", cmap="Reds", linewidth=0.8, ax=axes[0],
            edgecolor="0.8", norm=norm1, legend=False,
            missing_kwds={"color": "lightgray", "label": "No Data"})
axes[0].set_xlim(-2e6, 2.5e6)
axes[0].set_ylim(-2.4e6, 0.8e6)
axes[0].set_title("A. Annual Excess Deaths", fontsize=14, loc="left")
axes[0].axis("off")

# Colorbar A
cax1 = inset_axes(axes[0], width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0.0, -0.005, 1, 1), bbox_transform=axes[0].transAxes, borderpad=0)
sm1 = plt.cm.ScalarMappable(cmap="Reds", norm=norm1)
sm1._A = []
cbar1 = fig.colorbar(sm1, cax=cax1, orientation="horizontal")
cbar1.set_label("Annual Excess Deaths", fontsize=12)
tick_vals = [0, 100, 250, 500, 750, 1000, 1500]
cbar1.set_ticks(tick_vals)
cbar1.set_ticklabels([f"{int(t):,}" for t in tick_vals])

# Panel B: Per capita deaths
vmin2, vmax2 = merged["per_capita_median"].min(), merged["per_capita_median"].max()
norm2 = Normalize(vmin=vmin2, vmax=vmax2)
merged.plot(column="per_capita_median", cmap="YlOrRd", linewidth=0.8, ax=axes[1],
            edgecolor="0.8", norm=norm2, legend=False,
            missing_kwds={"color": "lightgray", "label": "No Data"})
axes[1].set_xlim(-2e6, 2.5e6)
axes[1].set_ylim(-2.4e6, 0.8e6)
axes[1].set_title("B. Excess Deaths per 100,000", fontsize=14, loc="left")
axes[1].axis("off")

# Colorbar B
cax2 = inset_axes(axes[1], width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0.0, -0.005, 1, 1), bbox_transform=axes[1].transAxes, borderpad=0)
sm2 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=norm2)
sm2._A = []
cbar2 = fig.colorbar(sm2, cax=cax2, orientation="horizontal")
cbar2.set_label("Excess Deaths per 100,000", fontsize=12)

# Save figure
plt.savefig(f"plots/figure_3_state_mortality_combined_{scenario}.png", dpi=300, bbox_inches="tight")
plt.close()
