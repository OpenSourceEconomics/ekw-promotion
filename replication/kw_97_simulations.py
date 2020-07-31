""" This script simulates the input for the example section in the handout. """
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


params, options, df_emp = rp.get_example_model("kw_97_extended")

# We want to reduce the computational burden for debugging purposes and our continuous
# integration pipeline.
if IS_DEBUG:
    options["n_periods"] = 10

simulate_func = rp.get_simulate_func(params, options)
df_sim = simulate_func(params)

pd.to_pickle(df_sim, "data-simulated.pkl")
pd.to_pickle(df_emp, "data-empirical.pkl")


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
