import helpers
import normaliser
import significance

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
    "pistol_rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "attack_rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "defense_rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    },
    "death_rounds": {
        "wins": 0,
        "total": 0,
        "rows": []
    }
}

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
        baseline_groups["pistol_rounds"]["total"] += 1
        baseline_groups["pistol_rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["pistol_rounds"]["wins"] += 1

    if round["side"] == "Attacker":
        baseline_groups["attack_rounds"]["total"] += 1
        baseline_groups["attack_rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["attack_rounds"]["wins"] += 1

    if round["side"] == "Defender":
        baseline_groups["defense_rounds"]["total"] += 1
        baseline_groups["defense_rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["defense_rounds"]["wins"] += 1

    if round["deaths"]:
        baseline_groups["death_rounds"]["total"] += 1
        baseline_groups["death_rounds"]["rows"].append(round)
        if round["won"]:
            baseline_groups["death_rounds"]["wins"] += 1

match_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "time"]
round_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "weapon", "took_opening_duel", "traded"]

def run_all_insights(baseline, only_significant=False):
    results = []
    inputs = match_insight_inputs if baseline == "matches" else round_insight_inputs

    for stat in inputs:
        results.extend(all_x_vs_baseline(stat, baseline, only_significant))

    vandal_vs_phantom_results = vandal_vs_phantom(only_significant=only_significant)
    money_spent_after_pistol_round_win_results = money_spent_after_pistol_round_win(only_significant=only_significant)

    if baseline == "matches":
        fast_requeue_after_win_vs_loss_results = fast_requeue_after_win_vs_loss(minutes=10,only_significant=only_significant)
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

def all_x_vs_baseline(group_by, baseline, only_significant=False):
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

        insight = significance.compare_two_groups(
            wins_a,
            total_a,
            wins_b,
            total_b,
            group_by,
            baseline,
            item,
            f"{baseline} not including {item}"
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

def vandal_vs_phantom(only_significant=False):
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
        "rounds with vandal and phantom",
        "rounds with Vandal",
        "rounds with Phantom"
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

def money_spent_after_pistol_round_win(only_significant=False):
    under_1200_wins = 0
    under_1200_total = 0
    over_1200_wins = 0
    over_1200_total = 0

    for index, round in enumerate(round_rows):
        if round["round_number"] in [2,14] and round_rows[index - 1]["won"]:
            if round["money_spent"] <= 1200:
                under_1200_total += 1
                if round["won"]:
                    under_1200_wins += 1
            elif round["money_spent"] >= 1200:
                over_1200_total += 1
                if round["won"]:
                    over_1200_wins += 1

    insight = significance.compare_two_groups(
        under_1200_wins,
        under_1200_total,
        over_1200_wins,
        over_1200_total,
        "money spent after winning pistol round",
        "round after pistol round win",
        "<1200 spent after winning pistol round",
        ">1200 spent after winning pistol round"
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

def fast_requeue_after_win_vs_loss(minutes=10, only_significant=False):
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
        f"matches started within {minutes} minutes of last match",
        f"Match started within {minutes} minutes of win",
        f"Match started within {minutes} minutes of loss"
    )
    if not only_significant:
        print(insight)
        return insight
    else:
        if insight["significance"] != "neutral":
            print(insight)
            return insight

