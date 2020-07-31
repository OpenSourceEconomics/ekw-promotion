"""Figures for the handout.

This module creates all figures for the handout. They are all used in the illustrative example.

"""
import shutil
import glob

from pathlib import Path
import os
import colorsys
import matplotlib.colors as mc

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import matplotlib as mpl

color_opts = ["colored", "black-white"]
jet_color_map = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
spec_dict = {
    "colored": {"colors": [None] * 4, "line": ["-"] * 3, "hatch": [""] * 3, "file": ""},
    "black-white": {
        "colors": ["#CCCCCC", "#808080", "k"],
        "line": ["-", "--", ":"],
        "hatch": ["", "OOO", "///"],
        "file": "-sw",
    },
}

PROJECT_DIR = Path(os.environ["PROJECT_DIR"])


def plot_decisions_by_age(df):
    """Plot decisions by age.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of decision data.

    Returns:
    --------
    savefig: pdf
        Figure saved as pdf file.

    """

    labels = ["blue_collar", "white_collar", "military", "school", "home"]
    coloring = {
        "blue_collar": "tab:blue",
        "white_collar": "tab:red",
        "military": "tab:purple",
        "school": "tab:orange",
        "home": "tab:green",
    }
    fig, ax = plt.subplots()

    shares = df_descriptives.loc[("empirical", slice(0, 10)), labels] * 100

    shares.plot.bar(stacked=True, ax=ax, width=0.8, color=list(coloring.values()))

    ax.set_xticklabels(np.arange(16, 27, 1), rotation="horizontal")
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    ax.set_ylabel("Share (in %)")
    ax.set_ylim(0, 100)

    ax.legend(
        labels=[label.split("_")[0].capitalize() for label in labels],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.04),
        ncol=5,
    )

    plt.savefig("fig-data-choices")


def plot_wage_moments(df, savgol=True):

    # TODO: Add filter feature.
    fig, ax = plt.subplots()

    y = df.loc[("empirical", slice(None)), "mean"].values
    ax.plot(y, label="Mean")

    ax.legend()

    fig.savefig("fig-data-wages-mean")


def plot_mechanism_subsidy(subsidies, levels):
    for color in color_opts:

        fig, ax = plt.subplots(1, 1)

        if color == "black-white":
            ax.fill_between(
                subsidies, levels, color=spec_dict[color]["colors"][1],
            )
        else:
            ax.fill_between(subsidies, levels)

        ax.yaxis.get_major_ticks()[0].set_visible(False)
        ax.set_ylabel("Average final schooling")
        ax.set_ylim([10, 19])

        ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
        ax.set_xlabel("Tuition subsidy")
        ax.set_xlim([None, 2000])

        if color == "black-white":
            fig.savefig("fig-policy-forecast-bw")
        else:
            fig.savefig("fig-policy-forecast")


def plot_mechanism_time(deltas, levels):
    for color in color_opts:

        fig, ax = plt.subplots(1, 1)

        if color == "black-white":
            ax.fill_between(
                deltas, levels, color=spec_dict[color]["colors"][1],
            )
        else:
            ax.fill_between(deltas, levels)

        ax.yaxis.get_major_ticks()[0].set_visible(False)
        ax.set_ylabel("Average final schooling")
        ax.set_ylim([10, 19])

        ax.set_xlabel(r"$\delta$")

        if color == "black-white":
            fig.savefig("fig-economic-mechanisms-bw")
        else:
            fig.savefig("fig-economic-mechanisms")


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


def plot_model_fit(df):
    # TODO: Add filter feature.

    for label in ["blue_collar", "mean"]:

        fig, ax = plt.subplots(1, 1)

        y = df.loc[("empirical", slice(None)), label].values
        ax.plot(range(50), y, label="Observed")

        y = df.loc[("simulated", slice(None)), label].values
        ax.plot(range(50), y, label="Simulated")

        ax.legend()

        fname = f"fig-model-fit-{label}"
        fig.savefig(fname.replace("_", "-"))


# We plot the model fit in and out of the support.
df_descriptives = pd.read_pickle("data-descriptives.pkl")

# We start with the observed data only.
plot_decisions_by_age(df_descriptives)
plot_wage_moments(df_descriptives)

# We than combine the descriptives from the observed and simulated data.
plot_model_fit(df_descriptives)

# We plot the counterfactual predictions of the model.
df_exploration = pd.read_pickle("model-exploration.pkl")

subsidies = (
    df_exploration.loc["subsidy", :].index.get_level_values("Change").to_numpy(np.float)
)
levels = df_exploration.loc[("subsidy", slice(None)), "level"].to_numpy(np.float)
plot_mechanism_subsidy(subsidies, levels)

deltas = (
    df_exploration.loc["delta", :].index.get_level_values("Change").to_numpy(np.float)
)
levels = df_exploration.loc[("delta", slice(None)), "level"].to_numpy(np.float)
plot_mechanism_time(deltas, levels)

# TODO: We need all figures as bw version, this is just to prototype workflow.
for fname in glob.glob("*.png"):
    if "bw" in fname:
        continue
    shutil.copy(fname, fname.replace(".png", "-bw.png"))
