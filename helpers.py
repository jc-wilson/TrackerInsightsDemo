import uuid
import json
import csv

def load_json_file(path):
    try:
        with open(path) as a:
            data = json.load(a)
        return data
    except FileNotFoundError:
        raise Exception(f"{path} does not exist")

def save_as_json(results):
    with open("results.json", "w", encoding="utf-8") as a:
        json.dump(results, a, indent=2)

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

# Converts uuids to names using lookup table
def uuid_to_display_name(value):
    if is_uuid(value):
        try:
            return lookup_table[value.lower()]
        except KeyError:
            return None
    else:
        return None

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

def format_value_label(group_by, value):
    if group_by == "solo_queue":
        return "Solo queue" if value else "Party queue"

    if group_by == "took_opening_duel":
        return "Rounds where you took the opening duel" if value else "Rounds where you didn't take the opening duel"

    if group_by == "traded":
        return "Traded rounds" if value else "Untraded rounds"

    return str(value)

# Formats the baseline labels
def baseline_label(baseline):
    labels = {
        "matches": "matches",
        "rounds": "rounds",
        "pistol rounds": "pistol rounds",
        "eco rounds": "eco rounds",
        "semi rounds": "semi-buy rounds",
        "full rounds": "full buy rounds",
        "attack rounds": "attack rounds",
        "defense rounds": "defense rounds",
        "death rounds": "rounds in which they died",
        "rounds with vandal or phantom": "rounds using either Vandal or Phantom",
        "round after pistol round win": "round after winning pistol round",
        "matches started within 10 minutes of last": "matches started within 10 minutes of last match",
    }
    return labels.get(baseline, str(baseline).replace("_", " "))

# Dynamically converts the statistical outputs of each insight into easily readable summaries
def build_summary_text(insight):
    group_by = insight["group_by"]
    baseline = baseline_label(insight["baseline"])
    significance = insight["significance"]
    low_sample = insight["low_sample"]

    stat_a = insight.get("stat_a")
    stat_b = insight.get("stat_b")
    value = insight.get("value")


    if group_by == "money spent after winning pistol round" or insight["baseline"] == "round after pistol round win":
        if significance == "positive":
            text = "This player wins more rounds after spending 1500 or fewer credits following a pistol-round win than they do after spending more than 1500"
        elif significance == "negative":
            text = "This player wins fewer rounds after spending 1500 or fewer credits following a pistol-round win than they do after spending more than 1500"
        else:
            text = "This player wins about the same number of rounds after spending 1500 or fewer credits following a pistol-round win as they do after spending more than 1500"


    elif "minutes of win or loss" in group_by or "minutes of last match" in insight["baseline"]:
        if significance == "positive":
            text = "This player wins more matches when starting the next game within 10 minutes of a win than they do when starting the next game within 10 minutes of a loss"
        elif significance == "negative":
            text = "This player wins fewer matches when starting the next game within 10 minutes of a win than they do when starting the next game within 10 minutes of a loss"
        else:
            text = "This player wins about the same number of matches when starting the next game within 10 minutes of a win as they do when starting the next game within 10 minutes of a loss"

    elif group_by == "map":
        if significance == "positive":
            text = f"This player wins more {stat_a} than they do on other maps"
        elif significance == "negative":
            text = f"This player wins fewer {stat_a} than they do on other maps"
        else:
            text = f"This player wins about the same number of {stat_a} as they do on other maps"

    elif group_by == "agent":
        if significance == "positive":
            text = f"This player wins more {stat_a} than they do on other agents"
        elif significance == "negative":
            text = f"This player wins fewer {stat_a} than they do on other agents"
        else:
            text = f"This player wins about the same number of {stat_a} as they do on other agents"

    elif group_by == "weapon":
        if significance == "positive":
            text = f"This player wins more {stat_a} than they do with other weapons"
        elif significance == "negative":
            text = f"This player wins fewer {stat_a} than they do with other weapons"
        else:
            text = f"This player wins about the same number of {stat_a} as they do with other weapons"

    elif group_by == "role":
        if significance == "positive":
            text = f"This player wins more {stat_a} than they do on other roles"
        elif significance == "negative":
            text = f"This player wins fewer {stat_a} than they do on other roles"
        else:
            text = f"This player wins about the same number of {stat_a} as they do on other roles"

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

    elif group_by == "vandal vs phantom":
        if stat_a:
            subject = "rounds started with a Vandal"
            comparison = "rounds started with a Phantom"
        else:
            subject = "rounds started with a Phantom"
            comparison = "rounds started with a Vandal"

        if significance == "positive":
            text = f"This player wins more {subject} than they do {comparison}"
        elif significance == "negative":
            text = f"This player wins fewer {subject} than they do {comparison}"
        else:
            text = f"This player wins about the same number of {subject} as they do {comparison}"

    elif group_by == "time":
        if stat_a:
            subject = "when they play during the hours of"
            comparison = "when they play outside these hours"
        else:
            subject = "when they play outside these hours"
            comparison = "when they play during these hours"

        if significance == "positive":
            text = f"This player wins more {stat_a} than {comparison}"
        elif significance == "negative":
            text = f"This player wins fewer {stat_a} than {comparison}"
        else:
            text = f"This player wins about the same number of {stat_a} as they do {comparison}"

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
