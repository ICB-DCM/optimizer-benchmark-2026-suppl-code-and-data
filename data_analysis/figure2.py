import colorsys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec

from lib import (
    N_PROBLEMS,
    OUTPUT_DIR,
    PROBLEM_OVERVIEW_PATH,
    SUBFIG_TITLE_KWARGS,
)


def par_coords_plot(ax_par):
    df = pd.read_csv(PROBLEM_OVERVIEW_PATH)
    assert len(df) == N_PROBLEMS

    cols2labels = {
        "n_observables": "Observables",
        "n_conditions": "Conditions",
        "n_est_parameters": "Parameters",
        "n_measurements": "Data points",
    }

    df.set_index("short", inplace=True)
    colors = df["problem_color"].values
    df = df[list(cols2labels)]

    assert (df > 0).all().all(), "All values must be non-negative."

    # cmap = plt.get_cmap("tab20")
    # colors = np.array([cmap(i / (N_PROBLEMS - 1)) for i in range(N_PROBLEMS)])
    cols = list(cols2labels.keys())
    labels = [cols2labels[c] for c in cols]
    num_cols = len(cols)

    # parallel coordinates + histograms

    # easier to work with log-values directly
    log_df = df.apply(np.log10)

    # draw histograms as horizontal bars
    for i, col in enumerate(cols):
        counts, bins = np.histogram(log_df[col])
        bin_lefts = bins[:-1]
        bin_rights = bins[1:]
        bin_heights = bin_rights - bin_lefts
        bin_centers = 0.5 * (bin_lefts + bin_rights)

        # same max width for all bars
        # max_bar_width = 0.4
        # widths = (counts.astype(float) / counts.max()) * max_bar_width
        # same scaling for all histograms, so widths are comparable
        widths = counts / 20.0

        # left edge so bars end at x == i and extend leftwards
        lefts = i - widths
        color = "lightgray"
        # draw bars
        ax_par.barh(
            bin_centers,
            widths,
            height=bin_heights,
            left=lefts,
            color=color,
            edgecolor="k",
            zorder=1 if i > 0 else 10,
        )

    # vertical line for each property
    for x in range(num_cols):
        ax_par.axvline(x, color="#eeeeee", zorder=0)

    # draw parallel coordinates lines
    for idx, (short_name, row) in enumerate(log_df.iterrows()):
        ax_par.plot(
            range(num_cols),
            row.values,
            color=colors[idx % len(colors)],
            alpha=0.8,
            zorder=3,
            label=short_name,
        )

    # ax_par.set_xlabel("Problem properties")
    ax_par.set_ylabel("Count")
    ax_par.set_xticks(range(num_cols))
    ax_par.set_xticklabels(labels, rotation=45, ha="right")
    ax_par.set_xlim(-0.5, num_cols - 1)
    ax_par.tick_params(axis="y")

    # show legend outside plot (right side)
    ax_par.legend(
        bbox_to_anchor=(1.05, 0.5),
        loc="center left",
        fontsize="small",
        # title="Problems",
        title_fontsize="medium",
        ncol=2,
    )

    ymin = log_df.min().min() * 0.9
    ymax = log_df.max().max() * 1.1
    ax_par.set_ylim(ymin, ymax)

    # custom log-scale-like ticks and labels for y-axis
    min_orig = df.min().min()
    max_orig = df.max().max()
    p_min = int(np.floor(np.log10(min_orig)))
    p_max = int(np.ceil(np.log10(max_orig)))

    # major ticks at powers of ten
    major_positions = []
    major_labels = []
    for p in range(p_min, p_max + 1):
        val = 10**p
        pos = np.log10(val)
        if ymin <= pos <= ymax:
            major_positions.append(pos)
            major_labels.append(str(int(val)))

    if len(major_positions) > 0:
        ax_par.set_yticks(major_positions)
        ax_par.set_yticklabels(major_labels)

    # minor ticks
    minor_positions = []
    # 2..9, 20...90,
    for p in range(0, p_max):
        for m in range(2, 10):
            val = m * (10**p)
            # only include values >= 1 and up to the max original value
            if val < 1:
                continue
            pos = np.log10(val)
            if val > max_orig:
                minor_positions.append(pos)
                break
            if ymin <= pos <= ymax:
                minor_positions.append(pos)

    if len(minor_positions) > 0:
        ax_par.set_yticks(sorted(minor_positions), minor=True)
        ax_par.tick_params(axis="y", which="minor", length=4, labelleft=False)

    # right y-axis without labels
    ax_right = ax_par.twinx()
    ax_right.set_ylim(ax_par.get_ylim())
    if len(major_positions) > 0:
        ax_right.set_yticks(major_positions)
        ax_right.tick_params(axis="y", labelright=False)
    if len(minor_positions) > 0:
        ax_right.set_yticks(sorted(minor_positions), minor=True)
        ax_right.tick_params(
            axis="y", which="minor", length=4, labelright=False
        )
    ax_right.yaxis.set_label_position("right")
    ax_right.spines["right"].set_visible(True)


def desaturate(color, factor=0.5):
    """Desaturate a color by a given factor."""
    r, g, b, a = color
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l, s * factor)
    return r, g, b, a


def lighten(color, amount=0.4):
    color = np.array(color)
    # blend with white
    color[:3] = 1 - amount * (1 - color[:3])
    return color


def features_heatmap(ax: plt.Axes):
    """Create heatmap of problem features."""
    import seaborn as sns

    df = pd.read_csv(PROBLEM_OVERVIEW_PATH)
    assert len(df) == N_PROBLEMS

    df.loc[
        df.error_model_type == "parameter- and state-dependent",
        "error_model_type",
    ] = "parameter- and\nstate-dependent"
    df.loc[
        df.error_model_type == "parameter-dependent",
        "error_model_type",
    ] = "parameter-\ndependent"

    cols = ["initial_condition_type", "error_model_type"]

    counts = df.groupby(cols).size().reset_index(name="count")
    pivot = (
        counts.pivot(index=cols[1], columns=cols[0], values="count")
        .fillna(0)
        .astype(int)
    )

    sns.heatmap(
        pivot,
        ax=ax,
        # annot=annot,
        annot=True,
        fmt="",
        cmap="Blues",
        linewidths=0.5,
        linecolor="white",
        cbar=False,
        square=True,
    )

    ax.set_xlabel("Initial condition")
    ax.set_ylabel("Error model")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)


def main():
    # 2x2, top: placeholder, bottom left: par coords, bottom right: heatmap
    plt.rcParams.update(
        {
            "font.size": 6,
            "figure.dpi": 300,
            "lines.linewidth": 0.8,
        }
    )
    fig = plt.figure(figsize=(18 / 2.54, 5), layout="constrained")
    gs = gridspec.GridSpec(
        2,
        2,
        height_ratios=[1, 1],
        # width_ratios=[0.8, 1.2],
        width_ratios=[1.3, 1],
        hspace=0.05,
        wspace=0.05,
        figure=fig,
    )
    ax_top = fig.add_subplot(gs[0, :])
    ax_bl = fig.add_subplot(gs[1, 0])
    ax_br = fig.add_subplot(gs[1, 1])

    # placeholder for top schema
    ax_top.set_facecolor("white")
    ax_top.axis("off")

    # problem dimensions, bottom left
    par_coords_plot(ax_bl)
    # error model / initial conditions, bottom right
    features_heatmap(ax_br)

    bbox = ax_bl.get_tightbbox()
    x_disp, y_disp = bbox.x0, bbox.y1  # left, top in display coords
    x_disp = 0
    y_disp += -40
    x_fig, y_fig = fig.transFigure.inverted().transform((x_disp, y_disp))

    fig.text(
        x_fig,
        0.99,
        "A   Benchmarking setup",
        **SUBFIG_TITLE_KWARGS,
        va="top",
        ha="left",
    )

    fig.text(
        x_fig,
        y_fig,
        "B   Dimensionality of problems",
        **SUBFIG_TITLE_KWARGS,
        ha="left",
        va="bottom",
    )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = ax_br.yaxis.get_label().get_window_extent(renderer=renderer)
    x_disp, y_disp = bbox.x0, bbox.y1
    x_fig, _ = fig.transFigure.inverted().transform((x_disp, y_disp))
    fig.text(
        x_fig,
        y_fig,
        "C   Selected technical properties",
        **SUBFIG_TITLE_KWARGS,
        ha="left",
        va="bottom",
    )

    for out_file in (
        OUTPUT_DIR / "figure2.pdf",
        OUTPUT_DIR / "figure2.svg",
    ):
        plt.savefig(out_file, bbox_inches="tight")
        print(f"Saved figure to {out_file}")


if __name__ == "__main__":
    main()
