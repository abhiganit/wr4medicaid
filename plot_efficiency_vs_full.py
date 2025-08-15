
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Load shapefile
gdf = gpd.read_file("shapefile/tl_2017_us_state.shp").to_crs(epsg=2163)
gdf = gdf.rename(columns={"NAME": "state"})

# Reposition Alaska and Hawaii
gdf.loc[gdf.state == "Alaska", "geometry"] = gdf.loc[gdf.state == "Alaska"].scale(0.2, 0.2, 0.2).translate(1.4e6, -4.5e6)
gdf.loc[gdf.state == "Hawaii", "geometry"] = gdf.loc[gdf.state == "Hawaii"].scale(0.8, 0.8, 0.8).translate(5e6, -1.35e6)

# Load mortality data
df_eff = pd.read_csv("results/state_mortality_ci_Efficiency_based_Exemption.csv").set_index("state")
df_full = pd.read_csv("results/state_mortality_ci_Full_Exemption.csv").set_index("state")

# Merge and calculate % averted
# Merge both datasets directly before joining with the GeoDataFrame
df_combined = df_eff[["median"]].rename(columns={"median": "eff_median"}).join(
    df_full["median"].rename("full_median")
)
# Then merge with gdf
merged = gdf.merge(df_combined, left_on="state", right_index=True, how="left")
merged["percent_averted"] = 100 * (merged["eff_median"] - merged["full_median"]) / merged["eff_median"]

#merged.loc[merged["median"] == 0, "percent_averted"] = 0

# Plot setup
os.makedirs("plots", exist_ok=True)
fig, axes = plt.subplots(2, 1, figsize=(10, 12), constrained_layout=False)
plt.subplots_adjust(hspace=0.25)

# Panel A: Efficiency-based excess deaths
vmin1, vmax1 = merged["eff_median"].min(), merged["eff_median"].max()
merged.plot(
    column="eff_median", cmap="Reds", ax=axes[0], linewidth=0.8, edgecolor="0.8",
    legend=False, vmin=vmin1, vmax=vmax1,
    missing_kwds={"color": "lightgray", "label": "No Data"}
)
axes[0].set_title("A. Excess Deaths: Efficiency-based Exemption", fontsize=14)
axes[0].axis("off")
axes[0].set_xlim(-2e6, 2.5e6)
axes[0].set_ylim(-2.4e6, 0.8e6)

cax1 = inset_axes(axes[0], width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0, -0.005, 1, 1), bbox_transform=axes[0].transAxes, borderpad=0)
sm1 = plt.cm.ScalarMappable(cmap="Reds", norm=Normalize(vmin=vmin1, vmax=vmax1))
sm1._A = []
cbar1 = fig.colorbar(sm1, cax=cax1, orientation="horizontal")
cbar1.set_label("Annual Excess Deaths", fontsize=12)

# Panel B: Percent averted if full exemption
vmin2, vmax2 = 0, 100
merged.plot(
    column="percent_averted", cmap="Blues", ax=axes[1], linewidth=0.8, edgecolor="0.8",
    legend=False, vmin=vmin2, vmax=vmax2,
    missing_kwds={"color": "lightgray", "label": "No Data"}
)
axes[1].set_title("B. Percent of Deaths Averted if Full Exemption Applied", fontsize=14)
axes[1].axis("off")
axes[1].set_xlim(-2e6, 2.5e6)
axes[1].set_ylim(-2.4e6, 0.8e6)

cax2 = inset_axes(axes[1], width="60%", height="3%", loc="lower center",
                  bbox_to_anchor=(0, -0.005, 1, 1), bbox_transform=axes[1].transAxes, borderpad=0)
sm2 = plt.cm.ScalarMappable(cmap="Blues", norm=Normalize(vmin=vmin2, vmax=vmax2))
sm2._A = []
cbar2 = fig.colorbar(sm2, cax=cax2, orientation="horizontal")
cbar2.set_label("% of Deaths Averted", fontsize=12)

# Save figure
plt.savefig("plots/figure_4_efficiency_vs_full.png", dpi=300, bbox_inches="tight")
plt.close()
