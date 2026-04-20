import helpers
import data_loader

# Builds a list of match dicts
def build_match_rows(match_data_path, puuid_data_path):
    match_rows = []
    matches_list = data_loader.load_match_data(match_data_path)
    target_puuid = data_loader.load_target_puuid(puuid_data_path)

    for match in matches_list:
        for player in match["players"]:
            if player["subject"] == target_puuid:
                match_row = {
                    "match_id": match["matchInfo"]["matchId"],
                    "started_at": match["matchInfo"]["gameStartMillis"],
                    "ended_at": match["matchInfo"]["gameStartMillis"] + match["matchInfo"]["gameLengthMillis"],
                    "map": helpers.map_url_to_display_name(match["matchInfo"]["mapId"]),
                    "result": None,
                    "team": player["teamId"],
                    "server": helpers.server_normaliser(match["matchInfo"]["gamePodId"]),
                    "agent_id": player["characterId"],
                    "agent_name": helpers.uuid_to_display_name(player["characterId"], "agent"),
                    "role": helpers.agent_to_role(player["characterId"]),
                    "party_id": player["partyId"],
                    "party_members": [],
                    "kills": player["stats"]["kills"],
                    "deaths": player["stats"]["deaths"],
                    "assists": player["stats"]["assists"],
                    "score": player["stats"]["score"],
                    "damage": None,
                    "rounds_played": player["stats"]["roundsPlayed"],
                    "abilities": player["stats"]["abilityCasts"],
                }

                # Checks if target player won, drew, or lost game
                team_rounds = []
                for team in match["teams"]:
                    if team["teamId"] == match_row["team"]:
                        if team["won"]:
                            match_row["result"] = "won"
                        else:
                            team_rounds.append(team["roundsWon"])
                    else:
                        team_rounds.append(team["roundsWon"])
                if len(team_rounds) == 2 and match_row["result"] != "won":
                    if team_rounds[0] == team_rounds[1]:
                        match_row["result"] = "draw"
                    else:
                        match_row["result"] = "lost"

                # Adds target player's teammates and party members to lists
                teammates = []
                for player2 in match["players"]:
                    if player2["partyId"] == match_row["party_id"] and player2["subject"] != target_puuid:
                        match_row["party_members"].append({"puuid": player2["subject"],
                                                           "username": f"{player2['gameName']}#{player2['tagLine']}"})
                    if player2["teamId"] == match_row["team"]:
                        teammates.append(player2["subject"])


                dealt_damage = 0
                for damage in player["roundDamage"]:
                    if damage["receiver"] not in teammates:
                        dealt_damage += damage["damage"]
                match_row["damage"] = dealt_damage

                match_rows.append(match_row)

    return match_rows

# Builds a list of round dicts
def build_round_rows(match_data_path, puuid_data_path):
    round_rows = []

    matches_list = data_loader.load_match_data(match_data_path)
    target_puuid = data_loader.load_target_puuid(puuid_data_path)

    for match in matches_list:
        match_info = {}
        for player in match["players"]:
            if player["subject"] == target_puuid:
                match_info = {
                    "match_id": match["matchInfo"]["matchId"],
                    "match_result": None,
                    "server": helpers.server_normaliser(match["matchInfo"]["gamePodId"]),
                    "map": helpers.map_url_to_display_name(match["matchInfo"]["mapId"]),
                    "agent_id": player["characterId"],
                    "agent_name": helpers.uuid_to_display_name(player["characterId"], "agent"),
                    "role": helpers.agent_to_role(player["characterId"]),
                    "team": player["teamId"],
                    "party_id": player["partyId"],
                    "teammates": [],
                    "party_members": []
                }

                # Adds target player's teammates and party members to lists
                for player2 in match["players"]:
                    if player2["partyId"] == match_info["party_id"] and player2["subject"] != target_puuid:
                        match_info["party_members"].append({"puuid": player2["subject"],
                                                           "username": f"{player2['gameName']}#{player2['tagLine']}"})
                    if player2["teamId"] == match_info["team"]:
                        match_info["teammates"].append(player2["subject"])

                        # Checks if target player won, drew, or lost game
                        team_rounds = []
                        for team in match["teams"]:
                            if team["teamId"] == match_info["team"]:
                                if team["won"]:
                                    match_info["match_result"] = "won"
                                else:
                                    team_rounds.append(team["roundsWon"])
                            else:
                                team_rounds.append(team["roundsWon"])
                        if len(team_rounds) == 2 and match_info["match_result"] != "won":
                            if team_rounds[0] == team_rounds[1]:
                                match_info["match_result"] = "draw"
                            else:
                                match_info["match_result"] = "lost"

                for round in match["roundResults"]:
                    round_row = {
                        "match_id": match_info["match_id"],
                        "match_result": match_info["match_result"],
                        "server": match_info["server"],
                        "map": match_info["map"],
                        "agent_id": match_info["agent_id"],
                        "agent_name": match_info["agent_name"],
                        "role": match_info["role"],
                        "round_number": round["roundNum"] + 1,
                        "won_round": True if round["winningTeam"] == match_info["team"] else False,
                        "round_outcome": round["roundResult"],
                        "round_ceremony": round["roundCeremony"],
                        "spike_planted": True if "bombPlanter" in round.keys() else False,
                        "spike_defused": True if "bombDefuser" in round.keys() else False,
                        "plant_site": round["plantSite"],
                        "team": match_info["team"],
                        "side": round["winningTeamRole"] if round["winningTeam"] == match_info["team"] else helpers.opposite_side(round["winningTeamRole"]),
                        "kills": 0,
                        "deaths": 0,
                        "assists": 0,
                        "headshots": 0,
                        "bodyshots": 0,
                        "legshots": 0,
                        "received_headshots": 0,
                        "received_bodyshots": 0,
                        "received_legshots": 0,
                        "damage": 0,
                        "received_damage": 0,
                        "score": None,
                        "took_opening_duel": None,
                        "won_opening_duel": True if round["firstBloodPlayer"] == target_puuid else False,
                        "traded": None,
                        "money_before_buy": None,
                        "money_spent": None,
                        "money_remaining": None,
                        "loadout_value": None,
                        "weapon_name": None,
                        "weapon_id": None,
                        "armour_name": None,
                        "armour_id": None,
                        "kill_weapon_ids": [],
                        "kill_weapon_names": [],
                        "death_weapon_ids": [],
                        "death_weapon_names": [],
                        "was_afk": None
                    }

                    for player3 in round["playerStats"]:
                        if player3["subject"] not in match_info["teammates"] and player3["subject"] == round["firstBloodPlayer"]:
                            if player3["kills"][0]["victim"] == target_puuid:
                                round_row["took_opening_duel"] = True
                            else:
                                round_row["took_opening_duel"] = False

                        if player3["kills"]:
                            for kill in player3["kills"]:
                                if kill["victim"] == target_puuid:
                                    round_row["deaths"] += 1
                                    round_row["death_weapon_ids"].append(kill["finishingDamage"]["damageItem"])
                                if target_puuid in kill["assistants"] and kill["victim"] not in match_info["teammates"]:
                                    round_row["assists"] += 1
                        if player3["damage"]:
                            if player3["damage"]:
                                for damage in player3["damage"]:
                                    if damage["receiver"] == target_puuid:
                                        round_row["received_damage"] += damage["damage"]
                                        round_row["received_headshots"] += damage["headshots"]
                                        round_row["received_bodyshots"] += damage["bodyshots"]
                                        round_row["received_legshots"] += damage["legshots"]


                        if player3["subject"] == target_puuid:
                            if player3["kills"]:
                                for kill in player3["kills"]:
                                    if kill["victim"] not in match_info["teammates"]:
                                        round_row["kills"] += 1
                                        round_row["kill_weapon_ids"].append(kill["finishingDamage"]["damageItem"])
                            if player3["damage"]:
                                for damage in player3["damage"]:
                                    if damage["receiver"] not in match_info["teammates"]:
                                        round_row["damage"] += damage["damage"]
                                        round_row["headshots"] += damage["headshots"]
                                        round_row["bodyshots"] += damage["bodyshots"]
                                        round_row["legshots"] += damage["legshots"]

                            if player3["wasAfk"]:
                                round_row["was_afk"] = True
                            else:
                                round_row["was_afk"] = False

                            round_row["score"] = player3["score"]
                            round_row["weapon_id"] = player3["economy"]["weapon"]
                            round_row["loadout_value"] = player3["economy"]["loadoutValue"]
                            round_row["armour_id"] = player3["economy"]["armor"]
                            round_row["money_remaining"] = player3["economy"]["remaining"]
                            round_row["money_spent"] = player3["economy"]["spent"]
                            round_row["money_before_buy"] = player3["economy"]["spent"] + player3["economy"]["remaining"]

                            round_row["weapon_name"] = helpers.uuid_to_display_name(round_row["weapon_id"], "weapon")
                            round_row["armour_name"] = helpers.uuid_to_display_name(round_row["armour_id"], "armour")

                            for weapon in round_row["kill_weapon_ids"]:
                                round_row["kill_weapon_names"].append(helpers.uuid_to_display_name(weapon, "weapon"))
                            for weapon in round_row["death_weapon_ids"]:
                                round_row["death_weapon_names"].append(helpers.uuid_to_display_name(weapon, "weapon"))

                            if round_row["won_opening_duel"] == True:
                                round_row["took_opening_duel"] = True

                            round_rows.append(round_row)
        continue
    return round_rows