import insight_calculator
import helpers


# Valid baselines:
# "rounds"
# "matches"
# "pistol rounds"
# "eco rounds"
# "semi rounds"
# "full rounds"
# "attack rounds"
# "defense rounds"
# "death rounds"

baseline = "rounds"

# If set to True, only non-neutral insights are exported.
only_significant = False

# Insights with a sample size below this threshold will have a "low sample" disclaimer
minimum_sample_size = 50

helpers.save_as_json(insight_calculator.run_all_insights(
    baseline,
    only_significant=only_significant,
    minimum_sample_size=minimum_sample_size
))

helpers.results_to_csv("results.json")