import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Parameters
input_dir = "results"
output_dir = "plots/pcolor_supplement"
plots_per_page = 6
ncols = 2
nrows = 3

os.makedirs(output_dir, exist_ok=True)

# Get sorted state grid files
state_dirs = sorted(d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d)))
csv_files = [
    os.path.join(input_dir, state, "mortality_grid.csv")
    for state in state_dirs
    if os.path.exists(os.path.join(input_dir, state, "mortality_grid.csv"))
]

# Paginate 6 plots per page
for page_num, chunk in enumerate([csv_files[i:i + plots_per_page] for i in range(0, len(csv_files), plots_per_page)], 1):
    fig = plt.figure(figsize=(12, 16), constrained_layout=True)
    gs = gridspec.GridSpec(nrows, ncols, figure=fig, wspace=0.1, hspace=0.05)

    for i, file in enumerate(chunk):
        df = pd.read_csv(file)
        state = os.path.basename(os.path.dirname(file)).replace("_", " ")
        ax = fig.add_subplot(gs[i // ncols, i % ncols])

        # Prep data
        pivot = df.pivot(index="failure_to_report", columns="efficiency", values="median")
        X = pivot.columns.values
        Y = pivot.index.values
        Z = pivot.values

        # Contour plot
        cf = ax.contourf(X, Y, Z, levels=15, cmap="viridis_r")
        lines = ax.contour(X, Y, Z, levels=10, colors="black", linewidths=0.7)
        ax.clabel(lines, inline=True, fontsize=7, fmt="%.0f")

        ax.set_title(state, fontsize=16)
        ax.set_xlabel("Auto-Exemption Efficiency", fontsize=14)
        ax.set_ylabel("Non-compliance Rate", fontsize=14)

        ax.tick_params(labelsize=8)

        # Per-plot inset colorbar
        #cax = ax.inset_axes([1.05, 0.0, 0.03, 1.0])

        fig.colorbar(cf,label='Excess deaths (Annual)') # cax=cax)

    fig.savefig(os.path.join(output_dir, f"state_grid_page_{page_num}.png"), dpi=300)
    plt.close()
