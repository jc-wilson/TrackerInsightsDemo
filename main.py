import insight_calculator
import helpers


baselines = [
    "rounds",
    "matches",
    "pistol rounds",
    "eco rounds",
    "semi-buy rounds",
    "full-buy rounds",
    "attack rounds",
    "defense rounds",
    "death rounds",
    "opening death rounds"
]

# If set to True, only non-neutral insights are exported.
only_significant = False

# Insights with a sample size below this threshold will have a "low sample" disclaimer
minimum_sample_size = 20


all_insights = []



for baseline in baselines:
    all_insights.extend(insight_calculator.run_all_insights(
        baseline,
        only_significant=only_significant,
        minimum_sample_size=minimum_sample_size
    ))


helpers.save_as_json(all_insights)

helpers.results_to_csv("results.json")
