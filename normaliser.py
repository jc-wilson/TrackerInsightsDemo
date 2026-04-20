import helpers
import data_loader

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
                            match_row["result"] = "Won"
                        else:
                            team_rounds.append(team["roundsWon"])
                    else:
                        team_rounds.append(team["roundsWon"])
                if len(team_rounds) == 2 and match_row["result"] != "Won":
                    if team_rounds[0] == team_rounds[1]:
                        match_row["result"] = "Draw"
                    else:
                        match_row["result"] = "Lost"

                # Adds target player's teammates and party members to lists
                teammates = []
                for player2 in match["players"]:
                    if player2["partyId"] == match_row["party_id"]:
                        match_row["party_members"].append({"puuid": player2["subject"],
                                                           "username": f"{player2["gameName"]}#{player2["tagLine"]}"})
                    if player2["teamId"] == match_row["team"]:
                        teammates.append(player2["subject"])


                dealt_damage = 0
                for damage in player["roundDamage"]:
                    if damage["receiver"] not in teammates:
                        dealt_damage += damage["damage"]
                match_row["damage"] = dealt_damage

                match_rows.append(match_row)

    return match_rows