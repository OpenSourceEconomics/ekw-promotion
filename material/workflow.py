from estimagic.optimization.optimize import maximize
import respy as rp

# obtain model input
params, options, df = rp.get_example_model("kw_97_extended")

# process model specification
crit_func = rp.get_crit_func(params, options, df)
simulate = rp.get_simulate_func(params, options)

# perform calibration
results, params_rslt = maximize(crit_func, params, "nlopt_bobyqa")

# conduct analysis
df_rslt = simulate(params_rslt)
