import respy as rp
from estimagic import maximize

# obtain model input
params, options, df = rp.get_example_model("kw_97_extended_respy")

# process model specification
log_like = rp.get_log_like_func(params, options, df)
simulate = rp.get_simulate_func(params, options)

# perform calibration
results, params_rslt = maximize(log_like, params, "nlopt_bobyqa")

# conduct analysis
df_rslt = simulate(params_rslt)
