import uuid
import json
import csv

# Loads json files into memory
def load_json_file(path):
    try:
        with open(path) as a:
            data = json.load(a)
        return data
    except FileNotFoundError:
        raise Exception(f"{path} does not exist")

# Saves results to json file
def save_as_json(results):
    with open("results.json", "w", encoding="utf-8") as a:
        json.dump(results, a, indent=2)

# Converts results to csv file
def results_to_csv(results):
    with open(results, "r", encoding="utf-8") as b:
        result = json.load(b)

    if result:
        if isinstance(result, dict):
            result = [result]

        result.sort(key=lambda x: (x["low_sample"], -abs(x["z_score"])))

        for insight in result:
            for key in insight:
                if isinstance(insight[key], float):
                    insight[key] = round(insight[key], 2)

        with open("results.csv", "w", newline="", encoding="utf-8") as c:
            writer = csv.DictWriter(c, fieldnames=result[0].keys())
            writer.writeheader()
            writer.writerows(result)

# Loads all UUID json files on start up
cached_data = {
    "map": load_json_file("map_uuids.json"),
    "agent": load_json_file("agent_uuids.json"),
    "weapon": load_json_file("weapon_uuids.json"),
    "armour": load_json_file("armour_uuids.json")
}

# UUID/map url to display name lookup dict
lookup_table = {}
for file in cached_data.keys():
    if file == "map":
        for item in cached_data[file]["data"]:
            lookup_table[item["mapUrl"]] = item["displayName"]
    else:
        for item in cached_data[file]["data"]:
            lookup_table[item["uuid"].lower()] = item["displayName"]

# Converts uuids to names
def uuid_to_display_name(value):
    if is_uuid(value):
        try:
            return lookup_table[value.lower()]
        except KeyError:
            return None
    else:
        return None

# Converts map URL to name
def map_url_to_display_name(value):
    try:
        return lookup_table[value]
    except KeyError:
        return None

# Returns the provided agent's role
def agent_to_role(agent_uuid):
    agent_data = load_json_file("agent_uuids.json")
    for agent in agent_data["data"]:
        if agent["uuid"] == agent_uuid:
            return agent["role"]["displayName"]
    return None

# Checks if provided value is a UUID
def is_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

# Converts gamePodId string into server name
def server_normaliser(value):
    if isinstance(value, str):
        server = value.split("-")
        return server[4].capitalize()
    else:
        return None

# Returns opposite side to input
def opposite_side(side):
    if side == "Attacker":
        return "Defender"
    if side == "Defender":
        return "Attacker"
    return None

# Formats summary text dynamically
def format_value_label(group_by, value):
    if group_by == "solo_queue":
        return "Solo queue" if value else "Party queue"

    if group_by == "took_opening_duel":
        return "Rounds where you took the opening duel" if value else "Rounds where you didn't take the opening duel"

    if group_by == "traded":
        return "Traded rounds" if value else "Untraded rounds"

    return str(value)

# Formats summary text dynamically
def format_comparison_label(group_by, value):
    if group_by == "weapon":
        return "other weapons"
    if group_by == "agent":
        return "other agents"
    if group_by == "map":
        return "other maps"
    if group_by == "role":
        return "other roles"
    if group_by == "server":
        return "other servers"
    if group_by == "time":
        return "other time windows"
    if group_by == "solo_queue":
        return "when not solo queueing" if value else "when solo queueing"
    if group_by == "took_opening_duel":
        return "when they do not take the opening duel" if value else "when they do take the opening duel"
    if group_by == "traded":
        return "when they are not traded" if value else "when they are traded"
    if group_by == "weapon_comparison":
        return "the comparison weapon"
    if group_by == "money spent after pistol round win":
        return "after spending more than 1200 credits following a pistol-round win" if "<1200" in str(value) else "after spending 1200 or fewer credits following a pistol-round win"
    if group_by == "fast_requeue_after_win_vs_loss":
        return "after requeueing quickly from a loss" if "win" in str(value).lower() else "after requeueing quickly from a win"

    return f"other {group_by} values"


# Converts baseline labels to plural/phrases
def baseline_label(baseline):
    labels = {
        "matches": "matches",
        "rounds": "rounds",
        "pistol_rounds": "pistol rounds",
        "attack_rounds": "attack rounds",
        "defense_rounds": "defense rounds",
        "death_rounds": "rounds in which they died",
        "rounds_with_vandal_and_phantom": "rounds",
        "round after pistol round win": "rounds",
        "matches_started_within_10_minutes_of_last": "matches",
    }
    return labels.get(baseline, str(baseline).replace("_", " "))



# Builds summary text from insights
def build_summary_text(insight):
    group_by = insight["group_by"]
    baseline = baseline_label(insight["baseline"])
    significance = insight["significance"]
    low_sample = insight["low_sample"]

    stat_a = insight.get("stat_a")
    stat_b = insight.get("stat_b")
    value = insight.get("value")

    if group_by == "weapon_comparison":
        if significance == "positive":
            text = f"This player wins more {baseline} with {stat_a} than they do with {stat_b}"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} with {stat_a} than they do with {stat_b}"
        else:
            text = f"This player wins about the same number of {baseline} with {stat_a} as they do with {stat_b}"


    elif group_by == "money spent after winning pistol round" or insight["baseline"] == "round after pistol round win":
        if significance == "positive":
            text = "This player wins more rounds after spending 1200 or fewer credits following a pistol-round win than they do after spending more than 1200"
        elif significance == "negative":
            text = "This player wins fewer rounds after spending 1200 or fewer credits following a pistol-round win than they do after spending more than 1200"
        else:
            text = "This player wins about the same number of rounds after spending 1200 or fewer credits following a pistol-round win as they do after spending more than 1200"


    elif "minutes of win or loss" in group_by or "minutes of last match" in insight["baseline"]:
        if significance == "positive":
            text = "This player wins more matches when starting the next game within 10 minutes of a win than they do when starting the next game within 10 minutes of a loss"
        elif significance == "negative":
            text = "This player wins fewer matches when starting the next game within 10 minutes of a win than they do when starting the next game within 10 minutes of a loss"
        else:
            text = "This player wins about the same number of matches when starting the next game within 10 minutes of a win as they do when starting the next game within 10 minutes of a loss"

    elif group_by == "map":
        if significance == "positive":
            text = f"This player wins more {baseline} on {stat_a} than they do on other maps"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} on {stat_a} than they do on other maps"
        else:
            text = f"This player wins about the same number of {baseline} on {stat_a} as they do on other maps"

    elif group_by == "agent":
        if significance == "positive":
            text = f"This player wins more {baseline} on {stat_a} than they do on other agents"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} on {stat_a} than they do on other agents"
        else:
            text = f"This player wins about the same number of {baseline} on {stat_a} as they do on other agents"

    elif group_by == "weapon":
        if significance == "positive":
            text = f"This player wins more {baseline} with {stat_a} than they do with other weapons"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} with {stat_a} than they do with other weapons"
        else:
            text = f"This player wins about the same number of {baseline} with {stat_a} as they do with other weapons"

    elif group_by == "role":
        if significance == "positive":
            text = f"This player wins more {baseline} on {stat_a} than they do on other roles"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} on {stat_a} than they do on other roles"
        else:
            text = f"This player wins about the same number of {baseline} on {stat_a} as they do on other roles"

    elif group_by == "solo_queue":
        if stat_a:
            subject = "when solo queueing"
            comparison = "when not solo queueing"
        else:
            subject = "when not solo queueing"
            comparison = "when solo queueing"

        if significance == "positive":
            text = f"This player wins more {baseline} {subject} than they do {comparison}"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} {subject} than they do {comparison}"
        else:
            text = f"This player wins about the same number of {baseline} {subject} as they do {comparison}"

    elif group_by == "took_opening_duel":
        if stat_a:
            subject = "when they take the opening duel"
            comparison = "when they do not"
        else:
            subject = "when they do not take the opening duel"
            comparison = "when they do"

        if significance == "positive":
            text = f"This player wins more {baseline} {subject} than they do {comparison}"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} {subject} than they do {comparison}"
        else:
            text = f"This player wins about the same number of {baseline} {subject} as they do {comparison}"

    elif group_by == "traded":
        if stat_a:
            subject = "when they are traded"
            comparison = "when they are not"
        else:
            subject = "when they are not traded"
            comparison = "when they are"

        if significance == "positive":
            text = f"This player wins more {baseline} {subject} than they do {comparison}"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} {subject} than they do {comparison}"
        else:
            text = f"This player wins about the same number of {baseline} {subject} as they do {comparison}"

    else:
        label = str(stat_a if stat_a is not None else value).replace("_", " ")
        if significance == "positive":
            text = f"This player wins more {baseline} for {label}"
        elif significance == "negative":
            text = f"This player wins fewer {baseline} for {label}"
        else:
            text = f"This player wins about the same number of {baseline} for {label}"

    if low_sample:
        text += " (low sample)."
    else:
        text += "."

    return text
