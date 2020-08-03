"""Figures for the handout.

This module creates all figures for the handout. They are all used in the illustrative example.

"""
import os
import colorsys

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.colors as mc
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.signal import savgol_filter

PROJECT_DIR = Path(os.environ["PROJECT_DIR"])


def make_grayscale_cmap(cmap):
    """Return a grayscale version of given colormap.

    Parameters:
    -----------
    cmap: matplotlib.colors.LinearSegmentedColormap
        Matplotlib color map (see
        https://matplotlib.org/tutorials/colors/colormaps.html for available
        color maps).

    Returns:
    --------
    cmap: 'matplotlib.colors.LinearSegmentedColormap
        Grayscale version color map of the given non-grayscale color map.

    """

    cmap = plt.cm.get_cmap(cmap)
    colors = cmap(np.arange(cmap.N))

    # Conversion of RGBA to grayscale lum by RGB_weight
    # RGB_weight given by http://alienryderflex.com/hsp.html
    RGB_weight = [0.299, 0.587, 0.114]
    lum = np.sqrt(np.dot(colors[:, :3] ** 2, RGB_weight))
    colors[:, :3] = lum[:, np.newaxis]

    return cmap.from_list(cmap.name + "_grayscale", colors, cmap.N)


def make_color_lighter(color, amount=0.5):
    """Returns a brightened (darkened) color.

    Parameters:
    -----------
    color: matplotlib color string, hex string, RGB tuple
        Name of color that will be brightened.

    amount: positive float
        Amount the color should be brightened (<1) or darkened (>1).

    Returns:
    --------
    _color: matplotlib color string, hex string, RGB tuple
        Brightened-up color (same format).

    """

    try:
        _color = mc.cnames[color]
    except Exception:
        _color = color
    _color = colorsys.rgb_to_hls(*mc.to_rgb(_color))

    return colorsys.hls_to_rgb(_color[0], 1 - amount * (1 - _color[1]), _color[2])


def plot_decisions_by_age(df_descriptives, color="color"):
    """Share of individuals in each occupation at any period (age)."""

    fig, ax = plt.subplots()

    shares = df_descriptives.loc[("empirical", slice(0, 10)), labels] * 100

    shares.plot.bar(
        stacked=True, ax=ax, width=0.8, color=list(color_scheme[color].values())[:-1]
    )

    ax.set_xlabel("Age")
    ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")

    ax.set_ylabel("Share (in %)")
    ax.set_ylim(0, 100)
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    ax.legend(
        labels=[label.split("_")[0].capitalize() for label in labels],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.04),
        ncol=5,
    )

    plt.savefig(f"fig-data-choices{color_scheme[color]['extension']}")


def plot_average_wage(df, savgol=False, color="colors"):
    """Average of wages at any period."""

    fig, ax = plt.subplots()

    y = df.loc[("empirical", slice(10)), "average"].values
    ext = ""
    if savgol:
        y = savgol_filter(y, 3, 2)
        ext = "-savgol"

    ax.plot(range(11), y, color=color_scheme[color]["blue_collar"])

    ax.set_ylim(5_000, 30_000)

    ax.set_xlabel("Age")
    ax.xaxis.set_ticks(range(11))
    ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")

    ax.set_ylabel("Wage (in $ 1,000)", labelpad=20)
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: "{0:0,}".format(int(x / 1000)))
    )

    fig.savefig(f"fig-data-wages-average{ext}{color_scheme[color]['extension']}")


def plot_mechanism_subsidy(subsidies, levels, color="color"):
    """Effect tuition subsidy on average final schooling."""

    fig, ax = plt.subplots()

    ax.fill_between(
        subsidies, levels, color=color_scheme[color]["blue_collar"],
    )

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.set_ylabel("Average final schooling")
    ax.set_ylim([10, 19])

    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("Tuition subsidy")
    ax.set_xlim([None, 2000])

    fig.savefig(f"fig-policy-forecast{color_scheme[color]['extension']}")


def plot_mechanism_time(deltas, levels, color="color"):
    """Effect time preferences on average final schooling."""

    fig, ax = plt.subplots()

    ax.fill_between(deltas, levels, color=color_scheme[color]["blue_collar"])

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.set_ylabel("Average final schooling")
    ax.set_ylim([10, 12])

    ax.set_xlabel(r"$\delta$")

    fig.savefig(f"fig-economic-mechanisms{color_scheme[color]['extension']}")


def plot_model_fit(df, savgol=False, color="color"):

    for label in ["blue_collar", "average"]:

        fig, ax = plt.subplots()

        y = df.loc[("empirical", slice(10)), label].values
        if label == "blue_collar":
            y = y * 100

        ext = ""
        if savgol:
            y = savgol_filter(y, 5, 4)
            ext = "-savgol"

        ax.plot(
            range(11), y, label="Observed", color=color_scheme[color]["blue_collar"]
        )

        y = df.loc[("simulated", slice(10)), label].values
        ax.plot(range(11), y, label="Simulated", color=color_scheme[color]["school"])

        ax.legend(loc="upper left")

        ax.set_xlabel("Age")
        ax.xaxis.set_ticks(range(11))
        ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")

        if label == "blue_collar":
            ax.set_ylabel("Share (in %)")
            ax.set_ylim(0, 100)

        if label == "average":
            ax.set_ylim(5_000, 30_000)
            ax.set_ylabel("Wage (in $ 1,000)", labelpad=20)
            ax.get_yaxis().set_major_formatter(
                plt.FuncFormatter(lambda x, loc: "{0:0,}".format(int(x / 1000)))
            )

        fname = f"fig-model-fit-{label}{ext}{color_scheme[color]['extension']}"
        fig.savefig(fname.replace("_", "-"))


# Define the color schemes for "color" and "bw"
_cmap = make_grayscale_cmap("copper")
color_scheme = {
    "bw": {
        "blue_collar": _cmap(0.29),
        "white_collar": _cmap(0.16),
        "military": _cmap(0.51),
        "school": _cmap(0.93),
        "home": _cmap(0.76),
        "extension": "-bw",
    },
    "color": {
        "blue_collar": "tab:blue",
        "white_collar": "tab:red",
        "military": "tab:purple",
        "school": "tab:orange",
        "home": "tab:green",
        "extension": "",
    },
}

# Ordering OSE convention: blue-collar, white-collar, military, school, home
labels = ["blue_collar", "white_collar", "military", "school", "home"]

# We plot the model fit in and out of the support.
df_descriptives = pd.read_pickle("data-descriptives.pkl")

# We start with the observed data only.
for col_scheme in ["color", "bw"]:

    plot_decisions_by_age(df_descriptives, color=col_scheme)

    plot_average_wage(df_descriptives, savgol=True, color=col_scheme)
    plot_average_wage(df_descriptives, savgol=False, color=col_scheme)

    # We than combine the descriptives from the observed and simulated data.
    plot_model_fit(df_descriptives, savgol=True, color=col_scheme)
    plot_model_fit(df_descriptives, savgol=False, color=col_scheme)

# We plot the counterfactual predictions of the model.
df_exploration = pd.read_pickle("model-exploration.pkl")

subsidies = (
    df_exploration.loc["subsidy", :].index.get_level_values("Change").to_numpy(np.float)
)
levels = df_exploration.loc[("subsidy", slice(None)), "level"].to_numpy(np.float)
plot_mechanism_subsidy(subsidies, levels)
plot_mechanism_subsidy(subsidies, levels, "bw")

deltas = (
    df_exploration.loc["delta", :].index.get_level_values("Change").to_numpy(np.float)
)
levels = df_exploration.loc[("delta", slice(None)), "level"].to_numpy(np.float)
plot_mechanism_time(deltas, levels)
plot_mechanism_time(deltas, levels, "bw")
