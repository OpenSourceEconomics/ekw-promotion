"""Figures for the handout.

This module creates all figures for the handout. They are all used in the illustrative example.

"""
from pathlib import Path
import os
import colorsys
import matplotlib.colors as mc
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import respy as rp

from itertools import compress
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

    shares = (
        df.groupby("Age").Choice.value_counts(normalize=True).unstack()[labels] * 100
    )
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

    plt.savefig("fig-observed-decisions-age")


def plot_wage_moments(df, savgol=True):
    """Plot mean and std of observed wages in blue, white, and military.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe consisting of sample data.

    savgol: Boolean
        Application of Savitzky Golay Filtering.

    References:
    -----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688

    """

    minimum_observations = 10
    wage_categories = ["blue_collar", "white_collar", "military"]
    wage_colors = {
        "blue_collar": "tab:blue",
        "white_collar": "tab:red",
        "military": "tab:purple",
    }

    wage_moments = (
        df.groupby(["Age", "Choice"])["Wage"].describe()[["mean", "std"]].unstack()
    )

    for moment in ["mean", "std"]:
        fig, ax = plt.subplots()

        if moment == "mean":
            color_scale = 1
            label_moment = "Average"
        if moment == "std":
            color_scale = 0.6
            label_moment = "Standard deviation"

        for wc in wage_categories:

            sufficient_boolean = list(
                *[
                    df.groupby(["Age"]).Choice.value_counts().unstack()[wc]
                    >= minimum_observations
                ]
            )
            non_sufficient_index = [
                i for i, bool in enumerate(sufficient_boolean) if bool is False
            ]
            _wage_moments = list(wage_moments[moment][wc])
            sufficient_wage_moments = list(compress(_wage_moments, sufficient_boolean))

            if savgol:
                y = list(savgol_filter(sufficient_wage_moments, 7, 3))
            else:
                y = sufficient_wage_moments

            for i, insertion in enumerate(non_sufficient_index):
                y.insert(insertion + i, np.nan)

            y_plot = pd.DataFrame(y, columns=[moment])
            y_plot.index = list(wage_moments[moment].index)

            ax.plot(
                y_plot,
                color=make_color_lighter(wage_colors[wc], color_scale),
                label=wc,
            )

        ax.legend(
            labels=[label.split("_")[0].capitalize() for label in wage_categories],
            loc="upper left",
            bbox_to_anchor=(0.2, 1.04),
            ncol=3,
        )

        ax.set_xticks(df["Age"].unique())
        ax.set_xlabel("Age")

        ax.set_ylabel(f"{label_moment} wage (in $ 1,000)", labelpad=20)
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{0:0,}".format(int(x / 1000)))
        )

        fig.savefig(f"{label_moment}-wages.png")


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


_, _, df_emp = rp.get_example_model("kw_97_extended")
df_emp["Age"] = df_emp.index.get_level_values(1) + 16

plot_decisions_by_age(df_emp)
plot_wage_moments(df_emp)

df_descriptives = pd.read_pickle("data-descriptives.pkl")

df = pd.read_pickle("mechanisms-subsidy.pkl")
subsidies = df.index.to_numpy(dtype=np.float)
levels = df.loc[:, "Level"].to_numpy(dtype=np.float)
plot_mechanism_subsidy(subsidies, levels)

df = pd.read_pickle("mechanisms-time.pkl")
deltas = df.index.to_numpy(dtype=np.float)
levels = df.loc[:, "Level"].to_numpy(dtype=np.float)
plot_mechanism_time(deltas, levels)
