"""Figures for the handout.

This module creates all figures for the handout. They are all used in the illustrative example.

"""
from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import numpy as np
import pandas as pd
from itertools import compress
import colorsys
import matplotlib.colors as mc
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import respy as rp
import pandas as pd
PROJECT_DIR = Path(os.environ["PROJECT_DIR"])
from itertools import compress


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

    shares = df.groupby("Age").Choice.value_counts(normalize=True).unstack()[labels] * 100
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
    wage_colors = {"blue_collar": "tab:blue", "white_collar": "tab:red", "military": "tab:purple"}

    wage_moments = df.groupby(["Age", "Choice"])["Wage"].describe()[["mean", "std"]].unstack()

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
                *[df.groupby(["Age"]).Choice.value_counts().unstack()[wc] >= minimum_observations]
            )
            non_sufficient_index = [i for i, bool in enumerate(sufficient_boolean) if bool is False]
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
                y_plot, color=make_color_lighter(wage_colors[wc], color_scale), label=wc,
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


df = pd.read_pickle("data-empirical.pkl")
df["Age"] = df.index.get_level_values(1) + 16

plot_decisions_by_age(df)
plot_wage_moments(df)
