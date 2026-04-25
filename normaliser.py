import helpers
import data_loader
from datetime import datetime

def distance_bucket(distance):
    if distance is None:
        return None
    if distance <= 5:
        return "0-5m"
    if distance <= 10:
        return "5-10m"
    if distance <= 20:
        return "10-20m"
    return "20m+"

# Builds a list of match dicts
def build_match_rows(match_data_path, puuid_data_path):
    match_rows = []
    matches_list = sorted(
        data_loader.load_match_data(match_data_path),
        key=lambda match: match["matchInfo"]["gameStartMillis"]
    )
    target_puuid = data_loader.load_target_puuid(puuid_data_path)

    for match in matches_list:
        for player in match["players"]:
            if player["subject"] == target_puuid:
                match_row = {
                    "match_id": match["matchInfo"]["matchId"],
                    "started_at": match["matchInfo"]["gameStartMillis"],
                    "ended_at": match["matchInfo"]["gameStartMillis"] + match["matchInfo"]["gameLengthMillis"],
                    "fast_requeue_after_loss": False,
                    "fast_requeue_after_win": False,
                    "hour": int(datetime.fromtimestamp(int(match["matchInfo"]["gameStartMillis"]) / 1000).strftime("%H")),
                    "time": None,
                    "map": helpers.map_url_to_display_name(match["matchInfo"]["mapId"]),
                    "result": None,
                    "won": False,
                    "team": player["teamId"],
                    "server": helpers.server_normaliser(match["matchInfo"]["gamePodId"]),
                    "agent_id": player["characterId"],
                    "agent": helpers.uuid_to_display_name(player["characterId"]),
                    "role": helpers.agent_to_role(player["characterId"]),
                    "party_id": player["partyId"],
                    "party_members": [],
                    "solo_queue": True,
                    "kills": player["stats"]["kills"],
                    "deaths": player["stats"]["deaths"],
                    "assists": player["stats"]["assists"],
                    "score": player["stats"]["score"],
                    "damage": None,
                    "rounds_played": player["stats"]["roundsPlayed"],
                    "abilities": player["stats"]["abilityCasts"],
                }

                if match_rows:
                    previous_match = match_rows[-1]
                    gap = match_row["started_at"] - previous_match["ended_at"]

                    if gap < 10 * 60 * 1000:
                        if previous_match["won"]:
                            match_row["fast_requeue_after_win"] = True
                        else:
                            match_row["fast_requeue_after_loss"] = True

                if 0 <= match_row["hour"] < 6:
                    match_row["time"] = "00-06"
                elif 6 <= match_row["hour"] < 12:
                    match_row["time"] = "06-12"
                elif 12 <= match_row["hour"] < 18:
                    match_row["time"] = "12-18"
                elif 18 <= match_row["hour"] < 24:
                    match_row["time"] = "18-00"

                # Checks if target player won, drew, or lost game
                team_rounds = []
                for team in match["teams"]:
                    if team["teamId"] == match_row["team"]:
                        if team["won"]:
                            match_row["result"] = "won"
                            match_row["won"] = True
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

                if match_row["party_members"]:
                    match_row["solo_queue"] = False

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
        for player in match["players"]:
            if player["subject"] == target_puuid:
                match_info = {
                    "match_id": match["matchInfo"]["matchId"],
                    "match_result": None,
                    "server": helpers.server_normaliser(match["matchInfo"]["gamePodId"]),
                    "map": helpers.map_url_to_display_name(match["matchInfo"]["mapId"]),
                    "agent_id": player["characterId"],
                    "agent": helpers.uuid_to_display_name(player["characterId"]),
                    "role": helpers.agent_to_role(player["characterId"]),
                    "team": player["teamId"],
                    "party_id": player["partyId"],
                    "solo_queue": True,
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

                if match_info["party_members"]:
                    match_info["solo_queue"] = False

                for round in match["roundResults"]:
                    round_row = {
                        "match_id": match_info["match_id"],
                        "match_result": match_info["match_result"],
                        "server": match_info["server"],
                        "map": match_info["map"],
                        "agent_id": match_info["agent_id"],
                        "agent": match_info["agent"],
                        "role": match_info["role"],
                        "solo_queue": match_info["solo_queue"],
                        "teammates": match_info["teammates"],
                        "party_members": match_info["party_members"],
                        "round_number": round["roundNum"] + 1,
                        "won": True if round["winningTeam"] == match_info["team"] else False,
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
                        "took_opening_duel": True if round["firstBloodPlayer"] == target_puuid else False,
                        "won_opening_duel": True if round["firstBloodPlayer"] == target_puuid else False,
                        "first_death_location": None,
                        "teammate_locations_at_first_death": [],
                        "first_death_nearest_teammate_distance": None,
                        "first_death_nearest_teammate_distance_bucket": None,
                        "death_locations": [],
                        "teammate_locations_at_death": [],
                        "death_nearest_teammate_distance": None,
                        "death_nearest_teammate_distance_bucket": None,
                        "traded": False,
                        "money_before_buy": None,
                        "money_spent": None,
                        "money_remaining": None,
                        "loadout_value": None,
                        "money_spent_after_pistol_round_win": None,
                        "enemy_team_loadout_value": 0,
                        "weapon": None,
                        "weapon_id": None,
                        "armour": None,
                        "armour_id": None,
                        "kill_weapon_ids": [],
                        "kill_weapon_names": [],
                        "death_weapon_ids": [],
                        "death_weapon_names": [],
                        "was_afk": None,
                    }

                    death_times = []
                    killers = []

                    for player3 in round["playerStats"]:
                        # Determines whether player took and/or won the opening duel.
                        if player3["subject"] not in match_info["teammates"] and player3["subject"] == round["firstBloodPlayer"]:
                            if player3["kills"][0]["victim"] == target_puuid:
                                round_row["took_opening_duel"] = True
                                round_row["first_death_location"] = player3["kills"][0]["victimLocation"]
                                for player4 in player3["kills"][0]["playerLocations"]:
                                    if player4["subject"] in match_info["teammates"]:
                                        round_row["teammate_locations_at_first_death"].append(player4["location"])
                            else:
                                round_row["took_opening_duel"] = False

                        # Tallies enemy team's loadout value
                        if player3["subject"] not in match_info["teammates"]:
                            round_row["enemy_team_loadout_value"] += player3["economy"]["loadoutValue"]

                        # Tallies player's deaths and also records death time and their killer for later trade status determination
                        if player3["kills"]:
                            for kill in player3["kills"]:
                                if kill["victim"] == target_puuid:
                                    round_row["deaths"] += 1
                                    round_row["death_locations"].append(kill["victimLocation"])
                                    death_times.append(kill["gameTime"])
                                    killers.append(kill["killer"])
                                    round_row["death_weapon_ids"].append(kill["finishingDamage"]["damageItem"])
                                    locs = []
                                    for loc in kill["playerLocations"]:
                                        if loc["subject"] in match_info["teammates"]:
                                            locs.append(loc["location"])
                                    round_row["teammate_locations_at_death"].append(locs)

                                if target_puuid in kill["assistants"] and kill["victim"] not in match_info["teammates"]:
                                    round_row["assists"] += 1

                        # Tallies the player's received damage, legshots, bodyshots, and headshots
                        if player3["damage"]:
                            if player3["damage"]:
                                for damage in player3["damage"]:
                                    if damage["receiver"] == target_puuid:
                                        round_row["received_damage"] += damage["damage"]
                                        round_row["received_headshots"] += damage["headshots"]
                                        round_row["received_bodyshots"] += damage["bodyshots"]
                                        round_row["received_legshots"] += damage["legshots"]

                        # Tallies player's kills, damage, legshots, bodyshots, and headshots
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

                            # Determines if player was AFK during this round or not
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

                            round_row["weapon"] = helpers.uuid_to_display_name(round_row["weapon_id"])
                            round_row["armour"] = helpers.uuid_to_display_name(round_row["armour_id"])

                            for weapon in round_row["kill_weapon_ids"]:
                                round_row["kill_weapon_names"].append(helpers.uuid_to_display_name(weapon))
                            for weapon in round_row["death_weapon_ids"]:
                                round_row["death_weapon_names"].append(helpers.uuid_to_display_name(weapon))

                            if round_row["won_opening_duel"] == True:
                                round_row["took_opening_duel"] = True

                    # Determines if player was traded within 3 seconds or not
                    if death_times and killers:
                        for index, death in enumerate(death_times):
                            if killers[index] not in round_row["teammates"]:
                                for player4 in round["playerStats"]:
                                    if player4["subject"] in round_row["teammates"]:
                                        for kill in player4["kills"]:
                                            if kill["victim"] == killers[index]:
                                                if (kill["gameTime"] - death) < 3000:
                                                    round_row["traded"] = True

                    # Calculates how far away nearest teammate was when the player died first
                    if round_row["took_opening_duel"] == True and round_row["won_opening_duel"] == False:
                        nearest_teammate_distance = 99999999999
                        for teammate_position in round_row["teammate_locations_at_first_death"]:
                            teammate_distance = helpers.coordinates_to_distance(
                                round_row["first_death_location"]["x"],
                                round_row["first_death_location"]["y"],
                                teammate_position["x"],
                                teammate_position["y"]
                            )
                            if teammate_distance < nearest_teammate_distance:
                                round_row["first_death_nearest_teammate_distance"] = teammate_distance
                                nearest_teammate_distance = teammate_distance
                        round_row["first_death_nearest_teammate_distance_bucket"] = distance_bucket(
                            round_row["first_death_nearest_teammate_distance"]
                        )

                    # Calculates how far away nearest teammate was when the player died
                    nearest_teammate_distance = 99999999999
                    if round_row["deaths"] >= 1 and round_row["teammate_locations_at_death"]:
                        for teammate_position in round_row["teammate_locations_at_death"][0]:
                            teammate_distance = helpers.coordinates_to_distance(
                                round_row["death_locations"][0]["x"],
                                round_row["death_locations"][0]["y"],
                                teammate_position["x"],
                                teammate_position["y"]
                            )
                            if teammate_distance < nearest_teammate_distance:
                                round_row["death_nearest_teammate_distance"] = teammate_distance
                                nearest_teammate_distance = teammate_distance
                        round_row["death_nearest_teammate_distance_bucket"] = distance_bucket(
                            round_row["death_nearest_teammate_distance"]
                        )

                    # Logs how much money was spent on the round after winning pistol round
                    if round_row["round_number"] in [2, 14]:
                        if round_rows[-1]["won"]:
                            round_row["money_spent_after_pistol_round_win"] = round_row["money_spent"]

                    round_rows.append(round_row)
        continue
    return round_rows
