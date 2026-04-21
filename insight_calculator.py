import normaliser
import significance

round_rows = normaliser.build_round_rows("match_data.json", "puuid_data.json")
match_rows = normaliser.build_match_rows("match_data.json", "puuid_data.json")

round_baseline_wins = 0
round_baseline_total = 0

match_baseline_wins = 0
match_baseline_total = 0

pistol_round_baseline_wins = 0
pistol_round_baseline_total = 0
pistol_round_rows = []

attack_round_baseline_wins = 0
attack_round_baseline_total = 0
attack_round_rows = []

defense_round_baseline_wins = 0
defense_round_baseline_total = 0
defense_round_rows = []

for match in match_rows:
    match_baseline_total += 1
    if match["won"]:
        match_baseline_wins += 1

for round in round_rows:
    round_baseline_total += 1
    if round["won"]:
        round_baseline_wins += 1
    if round["round_number"] in [1, 13]:
        pistol_round_baseline_total += 1
        pistol_round_rows.append(round)
        if round["won"]:
            pistol_round_baseline_wins += 1
    if round["side"] == "Attacker":
        attack_round_baseline_total += 1
        attack_round_rows.append(round)
        if round["won"]:
            attack_round_baseline_wins += 1
    if round["side"] == "Defender":
        defense_round_baseline_total += 1
        defense_round_rows.append(round)
        if round["won"]:
            defense_round_baseline_wins += 1

match_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "time"]
round_insight_inputs = ["server", "map", "role", "agent", "solo_queue", "weapon"]

def run_all_insights(baseline, only_significant=False):
    if baseline == "match":
        for insight in match_insight_inputs:
            all_x_vs_baseline(insight, baseline, only_significant)
    else:
        for insight in round_insight_inputs:
            all_x_vs_baseline(insight, baseline, only_significant)

def all_x_vs_baseline(filter, baseline, only_significant=False):
    items = {}
    if baseline == "round":
        rows = round_rows
        wins = round_baseline_wins
        total = round_baseline_total
    elif baseline == "match":
        rows = match_rows
        wins = match_baseline_wins
        total = match_baseline_total
    elif baseline == "pistol_round":
        rows = pistol_round_rows
        wins = pistol_round_baseline_wins
        total = pistol_round_baseline_total
    elif baseline == "attack":
        rows = attack_round_rows
        wins = attack_round_baseline_wins
        total = attack_round_baseline_total
    elif baseline == "defense":
        rows = defense_round_rows
        wins = defense_round_baseline_wins
        total = defense_round_baseline_total

    for row in rows:
        if row[filter] not in items.keys():
            items[row[filter]] = {}
            items[row[filter]]["total"] = 1
            if row["won"]:
                items[row[filter]]["wins"] = 1
            else:
                items[row[filter]]["wins"] = 0
        else:
            items[row[filter]]["total"] += 1
            if row["won"]:
                items[row[filter]]["wins"] += 1

    for item in items:
        insight = significance.compare_to_baseline(items[item]["wins"], items[item]["total"], wins, total)
        if only_significant == False:
            print(f"{filter}: {item} {insight}")
        elif only_significant == True and insight["significance"] != "neutral":
            print(f"{filter}: {item} {insight}")
        else:
            continue

def vandal_vs_phantom(only_significant=False):
    vandal_total = 0
    vandal_wins = 0
    phantom_total = 0
    phantom_wins = 0

    for round in round_rows:
        if round["weapon_name"].lower() == "vandal":
            vandal_total += 1
            if round["won"]:
                vandal_wins += 1
        if round["weapon_name"].lower() == "phantom":
            phantom_total += 1
            if round["won"]:
                phantom_wins += 1

    insight = significance.compare_two_groups(vandal_wins, vandal_total, phantom_wins, phantom_total)
    if not only_significant:
        print(insight)
    else:
        if insight["significance"] != "neutral":
            print(insight)

def entry_vs_baseline(only_significant=False):
    entry_wins = 0
    entry_total = 0

    for round in round_rows:
        if round["took_opening_duel"]:
            entry_total += 1
            if round["won"]:
                entry_wins += 1

    insight = significance.compare_to_baseline(entry_wins, entry_total, round_baseline_wins, round_baseline_total)
    if not only_significant:
        print(insight)
    else:
        if insight["significance"] != "neutral":
            print(insight)

def pistol_round_weapon_vs_baseline(only_significant=False):
    weapons = {}

    for round in round_rows:
        if round["round_number"] in [1, 13]:
            if round["weapon"] not in weapons.keys():
                weapons[round["weapon"]] = {}
                weapons[round["weapon"]]["weapon_total"] = 1
                if round["won_round"]:
                    weapons[round["weapon"]]["weapon_wins"] = 1
                else:
                    weapons[round["weapon"]]["weapon_wins"] = 0
            else:
                weapons[round["weapon"]]["weapon_total"] += 1
                if round["won_round"]:
                    weapons[round["weapon"]]["weapon_wins"] += 1

    for weapon in weapons:
        print(
            f"Weapon: {weapon} {significance.compare_to_baseline(weapons[weapon]["weapon_wins"], weapons[weapon]["weapon_total"], pistol_round_baseline_wins, pistol_round_baseline_total)}")

def money_spent_after_pistol_round_win():
    under_1200_wins = 0
    under_1200_total = 0
    over_1200_wins = 0
    over_1200_total = 0

    for index, round in enumerate(round_rows):
        if round["round_number"] in [1,13] and round["won"]:
            try:
                if round["match_id"] == round_rows[index + 1]["match_id"]:
                    if round_rows[index + 1]["money_spent"] <= 1200:
                        under_1200_total += 1
                        if round_rows[index + 1]["won"]:
                            under_1200_wins += 1
                    elif round_rows[index + 1]["money_spent"] >= 1200:
                        over_1200_total += 1
                        if round_rows[index + 1]["won"]:
                            over_1200_wins += 1
            except IndexError:
                pass

    print(significance.compare_two_groups(under_1200_wins, under_1200_total, over_1200_wins, over_1200_total))

def party_vs_baseline():
    party_wins = 0
    party_total = 0
    solo_wins = 0
    solo_total = 0

    for match in match_rows:
        if match["party_members"]:
            party_total += 1
            if match["result"] == "won":
                party_wins += 1
        else:
            solo_total += 1
            if match["result"] == "won":
                solo_wins += 1

    print(significance.compare_two_groups(party_wins, party_total, solo_wins, solo_total))

def agent_vs_baseline(agent):
    agent_wins = 0
    agent_total = 0

    for match in match_rows:
        if match["agent_name"] == agent:
            agent_total += 1
            if match["result"] == "won":
                agent_wins += 1

    print(significance.compare_to_baseline(agent_wins, agent_total, match_baseline_wins, match_baseline_total))

def map_vs_baseline(map):
    map_wins = 0
    map_total = 0

    for match in match_rows:
        if match["map"] == map:
            map_total += 1
            if match["result"] == "won":
                map_wins += 1

    print(significance.compare_to_baseline(map_wins, map_total, match_baseline_wins, match_baseline_total))

def hour_vs_baseline(start, end):
    chosen_hours_wins = 0
    chosen_hours_total = 0

    for match in match_rows:
        if start <= match["hour"] < end:
            chosen_hours_total += 1
            if match["result"] == "won":
                chosen_hours_wins += 1

    print(significance.compare_to_baseline(chosen_hours_wins, chosen_hours_total, match_baseline_wins, match_baseline_total))


