""" This script simulates the input for the example section in the handout.

This files creates the following files that are then used to create the proper plots for the
handout.

"""
from itertools import product

import pandas as pd
import numpy as np

import respy as rp

NUM_POINTS = 10
IS_DEBUG = True


def mechanism_wrapper(simulate, params, label, change):
    policy_params = params.copy()
    if label == "delta":
        policy_params.loc[("delta", "delta"), "value"] = change
    elif label == "suibsidy":
        policy_params.loc[("nonpec_school", "hs_graduate"), "value"] += change
    policy_df = simulate(policy_params)

    return policy_df.groupby("Identifier")["Experience_School"].max().mean()


def calc_choice_frequencies(df, source):
    """Compute choice frequencies."""
    df = df.groupby("Period").Choice.value_counts(normalize=True).unstack()
    df["Data"] = source
    df.set_index(["Data"], append=True, inplace=True)
    df = df.reorder_levels(["Data", "Period"])
    return df


def calc_wage_distribution(df, source):
    """Compute choice frequencies."""
    df = df.groupby(["Period"])["Wage"].describe()[["mean", "std"]]
    df.rename({"mean": "average"}, inplace=True)
    df["Data"] = source
    df.set_index(["Data"], append=True, inplace=True)
    df = df.reorder_levels(["Data", "Period"])
    return df


params, options, df_emp = rp.get_example_model("kw_97_extended")

# We want to reduce the computational burden for debugging purposes and our continuous
# integration pipeline.
if IS_DEBUG:
    options["n_periods"] = 10

simulate_func = rp.get_simulate_func(params, options)
df_sim = simulate_func(params)

# We store all needed descriptives about the simulated dataset.
index = list(product(["empirical", "simulated"], range(50)))
index = pd.MultiIndex.from_tuples(index, names=["Data", "Period"])
columns = ["blue_collar", "home", "military", "white_collar", "school", "average", "std"]
df_descriptives = pd.DataFrame(columns=columns, index=index)
df_descriptives.head()

for label, df in [("empirical", df_emp), ("simulated", df_sim)]:
    df_choice = calc_choice_frequencies(df, label)
    df_descriptives.update(df_choice)

    df_wage = calc_wage_distribution(df, label)
    df_descriptives.update(df_wage)

df_descriptives.to_pickle("data-descriptives.pkl")

# We evaluate the effect of a change in time preferences and a tuition subsidy.
subsidies = np.linspace(0, 2000, num=NUM_POINTS, dtype=int, endpoint=True)
deltas = np.linspace(0.910, 0.950, NUM_POINTS)

columns = ["level"]
index = list(product(["delta"], deltas)) + list(product(["subsidy"], subsidies))
index = pd.MultiIndex.from_tuples(index, names=["Experiment", "Change"])
df_mechanisms = pd.DataFrame(columns=columns, index=index)

for label, change in df_mechanisms.index:
    args = (simulate_func, params, label, change)
    df_mechanisms.loc[(label, change), :] = mechanism_wrapper(*args)
df_mechanisms.to_pickle("model-exploration.pkl")
