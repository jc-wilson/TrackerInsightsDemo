import normaliser

round_rows = normaliser.build_round_rows("match_data.json", "puuid_data.json")

print("Round rows:", len(round_rows))
print("Round wins:", sum(1 for row in round_rows if row["won_round"]))
print("Round losses:", sum(1 for row in round_rows if not row["won_round"]))
print("Opening duels taken:", sum(1 for row in round_rows if row["took_opening_duel"]))
print("Opening duels won:", sum(1 for row in round_rows if row["won_opening_duel"]))
print("Missing weapon names:", sum(1 for row in round_rows if row["weapon_name"] is None))
print("Missing side:", sum(1 for row in round_rows if row["side"] is None))
print("Missing score:", sum(1 for row in round_rows if row["score"] is None))
print("AFK rounds:", sum(1 for row in round_rows if row["was_afk"]))

match_rows = normaliser.build_match_rows("match_data.json", "puuid_data.json")

print("Match rows:", len(match_rows))
print("Match wins:", sum(1 for row in match_rows if row["result"] == "Won"))
print("Match losses:", sum(1 for row in match_rows if row["result"] == "Lost"))
print("Match draws:", sum(1 for row in match_rows if row["result"] == "Draw"))