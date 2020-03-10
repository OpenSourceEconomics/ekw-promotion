from estimagic.optimization.optimize import maximize
import respy as rp

# obtain model input
df, params, options = get_model_input()

# process model specification
crit_func = rp.get_crit_func(params, options, df)
simulate = rp.get_simulate_func(params, options)

# perform calibration
results, params_rslt = maximize(crit_func, params, "nlopt_bobyqa")

# conduct analysis
df_rslt = simulate(params_rslt)
