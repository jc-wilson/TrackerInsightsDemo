import normaliser
import significance

round_rows = normaliser.build_round_rows("match_data.json", "puuid_data.json")
match_rows = normaliser.build_match_rows("match_data.json", "puuid_data.json")

baseline_wins = 0
baseline_total = 0

for round in round_rows:
    baseline_total += 1
    if round["won_round"]:
        baseline_wins += 1

def vandal_vs_phantom():
    vandal_total = 0
    vandal_wins = 0
    phantom_total = 0
    phantom_wins = 0

    for round in round_rows:
        if round["weapon_name"].lower() == "vandal":
            vandal_total += 1
            if round["won_round"]:
                vandal_wins += 1
        if round["weapon_name"].lower() == "phantom":
            phantom_total += 1
            if round["won_round"]:
                phantom_wins += 1

    print(significance.compare_two_groups(vandal_wins, vandal_total, phantom_wins, phantom_total))

def entry_vs_baseline():
    entry_wins = 0
    entry_total = 0

    for round in round_rows:
        if round["took_opening_duel"]:
            entry_total += 1
            if round["won_round"]:
                entry_wins += 1

    print(significance.compare_to_baseline(entry_wins, entry_total, baseline_wins, baseline_total))

def money_spent_after_pistol_round_win():
    under_1200_wins = 0
    under_1200_total = 0
    over_1200_wins = 0
    over_1200_total = 0

    for index, round in enumerate(round_rows):
        if round["round_number"] in [1,13] and round["won_round"]:
            try:
                if round["match_id"] == round_rows[index + 1]["match_id"]:
                    if round_rows[index + 1]["money_spent"] <= 1200:
                        under_1200_total += 1
                        if round_rows[index + 1]["won_round"]:
                            under_1200_wins += 1
                    elif round_rows[index + 1]["money_spent"] >= 1200:
                        over_1200_total += 1
                        if round_rows[index + 1]["won_round"]:
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
        if match["result"] == "draw":
            continue
        if match["party_members"]:
            party_total += 1
            if match["result"] == "won":
                party_wins += 1
        else:
            solo_total += 1
            if match["result"] == "won":
                solo_wins += 1

    print(significance.compare_two_groups(party_wins, party_total, solo_wins, solo_total))
