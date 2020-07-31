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


def mechanism_wrapper(simulate, params, tuition_subsidy, label):
    policy_params = params.copy()
    policy_params.loc[label, "value"] += tuition_subsidy
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
columns = ["blue_collar", "home", "military", "white_collar", "school", "mean", "std"]
df_descriptives = pd.DataFrame(columns=columns, index=index)
df_descriptives.head()

for label, df in [("empirical", df_emp), ("simulated", df_sim)]:
    df_choice = calc_choice_frequencies(df, label)
    df_descriptives.update(df_choice)

    df_wage = calc_wage_distribution(df, label)
    df_descriptives.update(df_wage)

df_descriptives.to_pickle("data-descriptives.pkl")

# We evaluate the effect of a chance in time preferences.
label = ("delta", "delta")
deltas = np.linspace(0.910, 0.950, NUM_POINTS)

df = pd.DataFrame(columns=["Level"], index=deltas)
df.index.name = "Delta"

for delta in df.index.values:
    df.loc[delta, "Level"] = mechanism_wrapper(simulate_func, params, delta, label)

df.sort_index()
pd.to_pickle(df, "mechanisms-time.pkl")


# We evaluate the effect of tuition subsidy.
label = ("nonpec_school", "hs_graduate")
subsidies = np.linspace(0, 2000, num=NUM_POINTS, dtype=int, endpoint=True)

df = pd.DataFrame(columns=["Level"], index=subsidies)
df.index.name = "Subsidy"

for subsidy in df.index.values:
    df.loc[subsidy, "Level"] = mechanism_wrapper(simulate_func, params, subsidy, label)

df.sort_index()
pd.to_pickle(df, "mechanisms-subsidy.pkl")
