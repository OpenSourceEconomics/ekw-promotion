"""Figures for the handout.

This module creates all figures for the handout. They are all used in the illustrative example.

"""
from pathlib import Path
import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import respy as rp

PROJECT_DIR = Path(os.environ['PROJECT_DIR'])


"""Thi is the set up for the coloring options for the figures."""

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
        "colors": ["#808080", "#d3d3d3", "#A9A9A9", "#C0C0C0", "k"],
        "line": ["-", "--", ":"],
        "hatch": ["", "OOO", "///"],
        "file": "-sw",
    },
}

"""The following code produces data for the observed choices figure."""

params, options = rp.get_example_model('kw_94_two', with_data=False)

simulate = rp.get_simulate_func(params, options)
df = simulate(params)

stat = df.groupby('Identifier')['Experience_Edu'].max().mean()
print(f'Average education in baseline: {stat}')

df['Age'] = df['Period'] + 16
df['Choice'].cat.categories = ['Blue', 'White', 'Schooling', 'Home']
df.set_index(['Identifier', 'Period'], inplace=True, drop=True)

"""The following code creates the observed choices figure."""

for color in color_opts:

    fig, ax = plt.subplots()

    labels = ['Home', 'Schooling', 'Blue', 'White']
    shares = df.groupby('Age').Choice.value_counts(normalize=True).unstack()[labels] * 100
    if color == 'black-white':
        shares.plot.bar(
            stacked=True,
            ax=ax,
            width=0.8,
            color=[
                spec_dict[color]["colors"][0],
                spec_dict[color]["colors"][4],
                spec_dict[color]["colors"][2],
                spec_dict[color]["colors"][3]
            ]
        )
    else:
        shares.plot.bar(
        stacked=True,
        ax=ax,
        width=0.8
    )

    ax.legend(
        labels=labels, loc='lower center',
        bbox_to_anchor=(0.5, 1.04), ncol=4
    )

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.set_ylabel('Share (in %)')
    ax.set_ylim(0, 100)

    ax.set_xticklabels(np.arange(16, 55, 5), rotation='horizontal')
    ax.xaxis.set_ticks(np.arange(0, 40, 5))

    fig.savefig(
        f'fig-observed-choices'
        f'-{color}'
    )
    
"""The following code creates the policy forecast figure."""

params_sdcorr, options = rp.get_example_model('kw_94_two', with_data=False)
simulate_func = rp.get_simulate_func(params_sdcorr, options)
num_points = 10
edu_level = np.tile(np.nan, num_points)


def tuition_policy_wrapper_kw_94(simulate, params, tuition_subsidy):

    policy_params = params.copy()
    policy_params.loc[('nonpec_edu', 'at_least_twelve_exp_edu'), 'value'] += tuition_subsidy
    policy_df = simulate(policy_params)

    edu = policy_df.groupby('Identifier')['Experience_Edu'].max().mean()

    return edu


subsidies = np.linspace(0, 1500, num=num_points, dtype=int, endpoint=True)
for i, subsidy in enumerate(subsidies):
    edu_level[i] = tuition_policy_wrapper_kw_94(simulate_func, params_sdcorr, subsidy)

for color in color_opts:

    fig, ax = plt.subplots(1, 1)
    ax.plot(
        subsidies,
        edu_level,
        color=spec_dict[color]["colors"][1],
    )

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.set_ylabel('Average final schooling')
    ax.set_ylim([10, 19])

    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xlabel('Tuition subsidy')
    ax.set_xlim([None, 1600])

    fig.savefig(
        f'fig-policy-forecast'
        f'-{color}'
    )

"""The following code creates the economic mechanism figure."""


def time_preference_wrapper_kw_94(simulate, params, value):
    policy_params = params.copy()
    policy_params.loc[('delta', 'delta'), 'value'] = value
    policy_df = simulate(policy_params)

    edu = policy_df.groupby('Identifier')['Experience_Edu'].max().mean()

    return edu


deltas = np.linspace(0.945, 0.955, num_points)
for i, delta in enumerate(deltas):
    edu_level[i] = time_preference_wrapper_kw_94(simulate_func, params_sdcorr, delta)

    
for color in color_opts:
    
    fig, ax = plt.subplots(1, 1)
    ax.plot(
        deltas,
        edu_level,
        color=spec_dict[color]["colors"][1],
        ls=spec_dict[color]["line"][0],
    )

    ax.yaxis.get_major_ticks()[0].set_visible(False)
    ax.set_ylabel('Average final schooling')
    ax.set_ylim([10, 19])

    ax.set_xlabel(r'$\delta$')

    fig.savefig(
        f'fig-economic-mechanisms'
        f'-{color}'
    )
