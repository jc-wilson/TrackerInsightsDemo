import insight_calculator
import helpers


# Valid baselines:
# "rounds"
# "matches"
# "pistol_rounds"
# "attack_rounds"
# "defense_rounds"
# "death_rounds"

baseline = "matches"

# If set to True, only insights with an SD >1 will be included in the results.
only_significant = False

helpers.save_as_json(insight_calculator.run_all_insights(baseline, only_significant=only_significant))
helpers.results_to_csv("results.json")