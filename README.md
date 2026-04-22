# TrackerInsightsDemo

Small Python project for turning raw VALORANT match history into player-focused insight summaries.

The pipeline:

1. Loads raw match data from `match_data.json`
2. Normalises it into match-level and round-level rows
3. Compares grouped win rates across maps, agents, weapons, queue type, and situational splits
4. Writes the generated insights to `results.json` and `results.csv`

## Project Files

- `main.py`: entry point for generating output files
- `data_loader.py`: loads and validates raw input JSON
- `normaliser.py`: reshapes raw match data into analysis-ready rows
- `insight_calculator.py`: runs the insight comparisons
- `significance.py`: statistical helper functions
- `helpers.py`: formatting, lookups, JSON/CSV export helpers

## Requirements

- Python 3
- Local input files already present in the repository:
  - `match_data.json`
  - `puuid_data.json`
  - UUID lookup files for maps, agents, weapons, and armour

This project currently uses only Python's standard library, so there are no third-party runtime dependencies.

## Run

From the project root:

```powershell
python .\\main.py
```

This writes:

- `results.json`
- `results.csv`

## Notes

- `puuid_data.json` should contain a list of player PUUIDs; the first one is used by default.
- `main.py` currently runs the analysis with `baseline = "matches"` and `only_significant=False`.
