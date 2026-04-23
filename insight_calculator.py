import helpers
import normaliser
import significance

# Builds round and match rows using match_data.json and puuid_data.json
round_rows = normaliser.build_round_rows("match_data.json", "puuid_data.json")
match_rows = normaliser.build_match_rows("match_data.json", "puuid_data.json")

baseline_groups = {
    "rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "matches": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "pistol rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "eco rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "semi rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "full rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "attack rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "defense rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "death rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    }
}


# Builds baseline rows
for match in match_rows:
    baseline_groups["matches"]["total"] += 1
    baseline_groups["matches"]["rows"].append(match)
    if match["won"]:
        baseline_groups["matches"]["wins"] += 1

for round in round_rows:
    baseline_groups["rounds"]["total"] += 1
    baseline_groups["rounds"]["rows"].append(round)
    if round["won"]:
        baseline_groups["rounds"]["wins"] += 1

    if round["round_number"] in [1, 13]:
        baseline_groups["pistol rounds"]["total"] += 1
        baseline_groups["pistol rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["pistol rounds"]["wins"] += 1

    if round["side"] == "Attacker":
        baseline_groups["attack rounds"]["total"] += 1
        baseline_groups["attack rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["attack rounds"]["wins"] += 1

    if round["side"] == "Defender":
        baseline_groups["defense rounds"]["total"] += 1
        baseline_groups["defense rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["defense rounds"]["wins"] += 1

    if round["deaths"]:
        baseline_groups["death rounds"]["total"] += 1
        baseline_groups["death rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["death rounds"]["wins"] += 1

    # Eco rounds: 0-1500
    # Semi-buy rounds: 1501-3899
    # Full buy rounds: 3900+
    if round["loadout_value"] <= 1500:
        baseline_groups["eco rounds"]["total"] += 1
        baseline_groups["eco rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["eco rounds"]["wins"] += 1

    if 1500 < round["loadout_value"] < 3900:
        baseline_groups["semi rounds"]["total"] += 1
        baseline_groups["semi rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["semi rounds"]["wins"] += 1

    if 3900 <= round["loadout_value"]:
        baseline_groups["full rounds"]["total"] += 1
        baseline_groups["full rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["full rounds"]["wins"] += 1

# Available insights for matches and rounds
match_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "time"]
round_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "weapon", "took_opening_duel", "traded"]

# Runs all insight comparisons against the selected baseline
def run_all_insights(baseline, only_significant=False, minimum_sample_size=20):
    results = []
    inputs = match_insight_inputs if baseline == "matches" else round_insight_inputs

    for stat in inputs:
        results.extend(all_x_vs_baseline(stat, baseline, only_significant, minimum_sample_size))

    if baseline == "matches":
        fast_requeue_after_win_vs_loss_results = fast_requeue_after_win_vs_loss(minutes=10, only_significant=only_significant)
        if fast_requeue_after_win_vs_loss_results:
            results.append(fast_requeue_after_win_vs_loss_results)
    else:
        vandal_vs_phantom_results = vandal_vs_phantom(only_significant=only_significant)
        money_spent_after_pistol_round_win_results = money_spent_after_pistol_round_win(only_significant=only_significant)
        if vandal_vs_phantom_results:
            results.append(vandal_vs_phantom_results)
        if money_spent_after_pistol_round_win_results:
            results.append(money_spent_after_pistol_round_win_results)

    for insight in results:
        insight["summary_text"] = helpers.build_summary_text(insight)
    return results

# Compares one group against all remaining rows in the baseline
def all_x_vs_baseline(group_by, baseline, only_significant=False, minimum_sample_size=20):
    items = {}
    all_insights = []

    rows = baseline_groups[baseline]["rows"]
    wins = baseline_groups[baseline]["wins"]
    total = baseline_groups[baseline]["total"]

    for row in rows:
        if row[group_by] not in items.keys():
            items[row[group_by]] = {}
            items[row[group_by]]["total"] = 1
            if row["won"]:
                items[row[group_by]]["wins"] = 1
            else:
                items[row[group_by]]["wins"] = 0
        else:
            items[row[group_by]]["total"] += 1
            if row["won"]:
                items[row[group_by]]["wins"] += 1



    for item in items:
        wins_a = items[item]["wins"]
        total_a = items[item]["total"]
        wins_b = wins - wins_a
        total_b = total - total_a

        if total_a == 0 or total_b == 0:
            continue

        if group_by == "time":
            stat_a = f"{baseline} during {item}"
            stat_b = f"{baseline} not during {item}"
        elif group_by in ["solo_queue", "took_opening_duel", "traded"]:
            stat_a = item
            stat_b = not item
        else:
            stat_a = f"{baseline} on {item}"
            stat_b = f"{baseline} not on {item}"

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

        if only_significant == False:
            print(f"{group_by}: {item} {insight}")
            all_insights.append(insight)
        elif only_significant == True and insight["significance"] != "neutral":
            print(f"{group_by}: {item} {insight}")
            all_insights.append(insight)
        else:
            continue
    return all_insights

# Compares rounds in which the player started with a Vandal vs rounds in which the player started with a Phantom
def vandal_vs_phantom(only_significant=False, minimum_sample_size=20):
    vandal_total = 0
    vandal_wins = 0
    phantom_total = 0
    phantom_wins = 0

    for round in round_rows:
        if round["weapon"].lower() == "vandal":
            vandal_total += 1
            if round["won"]:
                vandal_wins += 1
        if round["weapon"].lower() == "phantom":
            phantom_total += 1
            if round["won"]:
                phantom_wins += 1

    insight = significance.compare_two_groups(
        vandal_wins,
        vandal_total,
        phantom_wins,
        phantom_total,
        "vandal vs phantom",
        "rounds",
        "rounds with Vandal",
        "rounds with Phantom",
        minimum_sample_size=minimum_sample_size
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

# Compares rounds after winning pistol round in which the player spent >1500 vs when they spent <=1500
def money_spent_after_pistol_round_win(only_significant=False, minimum_sample_size=20):
    under_1500_wins = 0
    under_1500_total = 0
    over_1500_wins = 0
    over_1500_total = 0

    for index, round in enumerate(round_rows):
        if round["round_number"] in [2,14] and round_rows[index - 1]["won"]:
            if round["money_spent"] <= 1500:
                under_1500_total += 1
                if round["won"]:
                    under_1500_wins += 1
            elif round["money_spent"] > 1500:
                over_1500_total += 1
                if round["won"]:
                    over_1500_wins += 1

    insight = significance.compare_two_groups(
        under_1500_wins,
        under_1500_total,
        over_1500_wins,
        over_1500_total,
        "money spent after winning pistol round",
        "rounds",
        "<=1500 spent after winning pistol round",
        ">1500 spent after winning pistol round",
        minimum_sample_size=minimum_sample_size
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

# Compares matches that the player got into within x amount of minutes of winning vs losing their last match (default 10)
def fast_requeue_after_win_vs_loss(minutes=10, only_significant=False, minimum_sample_size=20):
    after_win_wins = 0
    after_win_total = 0
    after_loss_wins = 0
    after_loss_total = 0

    sorted_matches = sorted(match_rows, key=lambda match: match["started_at"])
    for index, match in enumerate(sorted_matches):
        if index == 0:
            continue
        else:
            ms_gap = sorted_matches[index]["started_at"] - sorted_matches[index - 1]["ended_at"]
            if ms_gap > minutes * 60 * 1000:
                continue
            else:
                if sorted_matches[index - 1]["won"]:
                    after_win_total += 1
                    if sorted_matches[index]["won"]:
                        after_win_wins += 1
                else:
                    after_loss_total += 1
                    if sorted_matches[index]["won"]:
                        after_loss_wins += 1

    insight = significance.compare_two_groups(
        after_win_wins,
        after_win_total,
        after_loss_wins,
        after_loss_total,
        f"matches started within {minutes} minutes of win or loss",
        f"matches",
        f"Match started within {minutes} minutes of win",
        f"Match started within {minutes} minutes of loss",
        minimum_sample_size=minimum_sample_size
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

