"""Plots for data appendix."""
import sys

from material.career_decisions_analysis import get_average_wages
from material.career_decisions_analysis import get_choices
from material.career_decisions_analysis import get_df_transition_probabilities
from material.career_decisions_analysis import get_initial_schooling
from material.career_decisions_analysis import get_initial_schooling_activity
from material.career_decisions_analysis import get_prepare_career_decisions_data
from material.career_decisions_analysis import get_working_experience
from material.career_decisions_analysis import make_transition_matrix
from material.career_decisions_auxiliary import display_side_by_side
from material.career_decisions_plot import plot_decisions_by_age
from material.career_decisions_plot import plot_initial_schooling
from material.career_decisions_plot import plot_sample_size
from material.career_decisions_plot import plot_transition_heatmap
from material.career_decisions_plot import plot_wage_moments

sys.path.insert(0, "material/")
coloring = "color"

df = get_prepare_career_decisions_data("material/career-decisions.raw")
df = df.groupby("Identifier").apply(lambda x: get_working_experience(x))

df.head(5)  # plot first 5 years

#
plot_sample_size(df, coloring)  # already there

display_side_by_side(get_choices(df)["total"], get_choices(df)["share"])

plot_decisions_by_age(df, coloring)

get_average_wages(df)
plot_wage_moments(df, savgol=True, color=coloring)

get_initial_schooling(df)[0]
plot_initial_schooling(get_initial_schooling(df)[1], coloring)

get_initial_schooling_activity(df)

get_df_transition_probabilities(make_transition_matrix(df), "origin_to_destination")

get_df_transition_probabilities(make_transition_matrix(df), "destination_from_origin")

plot_transition_heatmap(make_transition_matrix(df), "origin_to_destination", coloring)

# Important Note on Transition Probabilities
make_transition_matrix(df, include_fifteen=True)

get_df_transition_probabilities(
    make_transition_matrix(df, include_fifteen=True),
    "origin_to_destination",
    save_include_fifteen=True,
)
