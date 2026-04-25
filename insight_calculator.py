import helpers
import normaliser
import significance
import insight_configs

# Builds round and match rows using match_data.json and puuid_data.json
round_rows = normaliser.build_round_rows("match_data.json", "puuid_data.json")
match_rows = normaliser.build_match_rows("match_data.json", "puuid_data.json")


def build_baseline_groups(round_rows, match_rows):
    baseline_groups = {}

    for name, config in insight_configs.BASELINE_CONFIGS.items():
        source_rows = round_rows if config["source"] == "rounds" else match_rows
        rows = [row for row in source_rows if config["filter"](row)]

        baseline_groups[name] = {
            "wins": sum(1 for row in rows if row["won"]),
            "total": len(rows),
            "rows": rows,
        }

    return baseline_groups


# Runs all insight comparisons against the selected baseline
def run_all_insights(baseline, only_significant=False, minimum_sample_size=20):
    results = []

    inputs = insight_configs.GROUP_INSIGHTS_BY_BASELINE.get(baseline, [])

    for stat in inputs:
        results.extend(
            all_x_vs_baseline(
                stat,
                baseline,
                only_significant,
                minimum_sample_size
            )
        )

    for config in insight_configs.COMPARISON_INSIGHTS:
        if config["baseline"] != baseline:
            continue

        insight = comparison_vs_comparison(
            config,
            baseline_groups[baseline]["rows"],
            only_significant=only_significant,
            minimum_sample_size=minimum_sample_size
        )

        if insight:
            results.append(insight)

    for insight in results:
        insight["summary_text"] = helpers.build_summary_text(insight)

    return results

baseline_groups = build_baseline_groups(round_rows, match_rows)

def comparison_vs_comparison(config, rows, only_significant=False, minimum_sample_size=20):
    wins_a = 0
    total_a = 0
    wins_b = 0
    total_b = 0

    for row in rows:
        if config["filter_a"](row):
            total_a += 1
            if row["won"]:
                wins_a += 1

        elif config["filter_b"](row):
            total_b += 1
            if row["won"]:
                wins_b += 1

    insight = significance.compare_two_groups(
        wins_a,
        total_a,
        wins_b,
        total_b,
        config["group_by"],
        config["baseline"],
        config["stat_a"],
        config["stat_b"],
        minimum_sample_size=minimum_sample_size
    )

    if not only_significant:
        return insight

    if insight["significance"] != "neutral":
        return insight

    return None


def average_x_in_win_vs_loss(group_by, baseline):
    items = {}
    rows = baseline_groups[baseline]["rows"]

    won_raw = []
    lost_raw = []

    for row in rows:
        if row[group_by] or row[group_by] == 0:
            if row["won"]:
                won_raw.append(row[group_by])
            else:
                lost_raw.append(row[group_by])

    if not len(won_raw):
        won_average = 0
    else:
        won_average = sum(won_raw) / len(won_raw)

    if not len(lost_raw):
        lost_average = 0
    else:
        lost_average = sum(lost_raw) / len(lost_raw)

    print(f"Won average: {round(won_average, 1)}")
    print(f"Lost average: {round(lost_average, 1)}")
    print(f"Won sample size: {len(won_raw)}")
    print(f"Lost sample size: {len(lost_raw)}")
    print(f"Sample Size: {len(won_raw) + len(lost_raw)}")

# Compares one group against all remaining rows in the baseline
def all_x_vs_baseline(group_by, baseline, only_significant=False, minimum_sample_size=20):
    items = {}
    all_insights = []

    rows = baseline_groups[baseline]["rows"]
    wins = baseline_groups[baseline]["wins"]
    total = baseline_groups[baseline]["total"]

    for row in rows:
        value = row.get(group_by)
        if value is None and group_by != "armour":
            continue

        if value not in items.keys():
            items[value] = {}
            items[value]["total"] = 1
            if row["won"]:
                items[value]["wins"] = 1
            else:
                items[value]["wins"] = 0
        else:
            items[value]["total"] += 1
            if row["won"]:
                items[value]["wins"] += 1



    for item in items:
        display_item = "No Armour" if group_by == "armour" and item is None else item
        wins_a = items[item]["wins"]
        total_a = items[item]["total"]
        wins_b = wins - wins_a
        total_b = total - total_a

        if total_a == 0 or total_b == 0:
            continue

        if group_by == "time":
            stat_a = f"{baseline} during {display_item}"
            stat_b = f"{baseline} not during {display_item}"
        elif group_by in ["solo_queue", "took_opening_duel", "traded"]:
            stat_a = display_item
            stat_b = not display_item
        else:
            stat_a = helpers.format_group_stat_label(group_by, baseline, display_item)
            stat_b = f"{baseline} not on {display_item}"

        insight = significance.compare_two_groups(
            wins_a,
            total_a,
            wins_b,
            total_b,
            group_by,
            baseline,
            stat_a,
            stat_b,
            minimum_sample_size=minimum_sample_size
        )

        if not only_significant:
            print(f"{group_by}: {item} {insight}")
            all_insights.append(insight)

        elif only_significant and insight["significance"] != "neutral":
            print(f"{group_by}: {item} {insight}")
            all_insights.append(insight)

        else:
            continue

    return all_insights
