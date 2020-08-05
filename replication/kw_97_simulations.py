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


def calc_choice_frequencies(df):
    """Compute choice frequencies."""
    df_choice = df.groupby("Period").Choice.value_counts(normalize=True).unstack()
    index = list(product(["probs"], df_choice.columns))
    df_choice.columns = pd.MultiIndex.from_tuples(index)
    return df_choice


def calc_wage_distribution_occupation(df):
    """Compute choice frequencies."""
    df_occ = df.groupby(["Period", "Choice"])["Wage"].describe()[["mean", "std"]]
    cond = df_occ.index.get_level_values("Choice").isin(["school", "home"])
    df_occ = df_occ[~cond]
    df_occ = df_occ.unstack()
    return df_occ


def calc_wage_distribution_overall(df):
    """Compute choice frequencies."""
    df_ove = df.groupby(["Period"])["Wage"].describe()[["mean", "std"]]
    df_ove["Choice"] = "all"
    df_ove.set_index(["Choice"], append=True, inplace=True)
    df_ove = df_ove.reorder_levels(["Period", "Choice"])
    df_ove = df_ove.unstack()
    return df_ove


params, options, df_emp = rp.get_example_model("kw_97_extended_respy")

# We want to reduce the computational burden for debugging purposes and our continuous
# integration pipeline.
if IS_DEBUG:
    options["n_periods"] = 12

simulate_func = rp.get_simulate_func(params, options)
df_sim = simulate_func(params)

df_descriptives = None

for label, df in [("empirical", df_emp), ("simulated", df_sim)]:

    df_occ = calc_wage_distribution_occupation(df)
    df_ove = calc_wage_distribution_overall(df)
    df_choice = calc_choice_frequencies(df)

    df_all = pd.concat([df_choice, df_occ, df_ove], axis=1)

    df_all["Data"] = label
    df_all.set_index(["Data"], append=True, inplace=True)
    df_all = df_all.reorder_levels(["Data", "Period"])
    df_descriptives = pd.concat([df_descriptives, df_all])

df_descriptives.index = df_descriptives.index.sort_values()
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
