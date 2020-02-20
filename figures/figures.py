""" Figures for the transdisciplinary talks.

This module creates all figures for the presentation in support of our transdisciplinary research
efforts.

"""
from pathlib import Path
import os

import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import respy as rp

PROJECT_DIR = Path(os.environ["PROJECT_DIR"])

# We label and format the different columns.
columns = ['Identifier', 'Age', 'Schooling', 'Choice', 'Wage']

params, options = rp.get_example_model("kw_94_one", with_data=False)

simulate = rp.get_simulate_func(params, options)
df = simulate(params)

df['Age'] = df['Period'] + 16
df.set_index(['Identifier', 'Period'], inplace=True, drop=True)
age_grid = df["Age"].unique()

df["Choice"].cat.categories = ['White', 'Blue', 'Schooling', 'Home']


fig, ax = plt.subplots()

columns = ["Home", "Schooling", "White", "Blue"]
shares = df.groupby("Age").Choice.value_counts(normalize=True).unstack()[columns]
shares.plot.bar(stacked=True, ax=ax, width=0.8)

labels = ["Home", "School", "White", "Blue"]
ax.legend(labels=labels, loc="lower center", bbox_to_anchor=(0.5, 1.04), ncol=4)

ax.set_ylabel("Share of individuals")
ax.set_ylim(0, 1)

ax.set_xticklabels(np.arange(16, 55, 5), rotation="horizontal")
ax.xaxis.set_ticks(np.arange(0, 40, 5))

ax.yaxis.get_major_ticks()[0].set_visible(False)

fig.savefig("fig-observed-choices")

params_sdcorr, options = rp.get_example_model("kw_94_one", with_data=False)
simulate_func = rp.get_simulate_func(params_sdcorr, options)


def tuition_policy_wrapper_kw_94(simulate, params, tuition_subsidy):

    policy_params = params.copy()
    policy_params.loc[("nonpec_edu", "at_least_twelve_exp_edu"), "value"] += tuition_subsidy
    policy_df = simulate(policy_params)

    edu = policy_df.groupby("Identifier")["Experience_Edu"].max().mean()

    return edu


num_points = 10
edu_level = np.tile(np.nan, num_points)
subsidies = np.linspace(0, 1500, num=num_points,dtype=int, endpoint=True)
for i, subsidy in enumerate(subsidies):
    edu_level[i] = tuition_policy_wrapper_kw_94(simulate_func, params_sdcorr, subsidy)

fig, ax = plt.subplots(1, 1)

x, y = subsidies, edu_level
ax.plot(x, y)

ax.yaxis.get_major_ticks()[0].set_visible(False)
ax.set_ylabel("Average schooling")
ax.set_ylim([12, 18])

ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
ax.set_xlabel("Tuition subsidy")
ax.set_xlim([None, 1600])

fig.savefig('fig-policy-evaluation')

params_sdcorr, options = rp.get_example_model("kw_94_one", with_data=False)
simulate_func = rp.get_simulate_func(params_sdcorr, options)


def time_preference_wrapper_kw_94(simulate, params, value):
    policy_params = params.copy()
    policy_params.loc[("delta", "delta"), "value"] = value
    policy_df = simulate(policy_params)

    edu = policy_df.groupby("Identifier")["Experience_Edu"].max().mean()

    return edu


num_points = 10
edu_level = np.tile(np.nan, num_points)
deltas = np.linspace(0.945, 0.955, num=num_points, endpoint=True)
for i, delta in enumerate(deltas):
    edu_level[i] = time_preference_wrapper_kw_94(simulate_func, params_sdcorr, delta)

fig, ax = plt.subplots(1, 1)

x, y = deltas, edu_level
ax.plot(x, y)

ax.yaxis.get_major_ticks()[0].set_visible(False)
ax.set_ylabel("Average schooling")
ax.set_ylim([10, 19])

ax.set_xlabel(r"$\delta$")

fig.savefig('fig-economic-mechanisms')