import uuid
import json

# Loads json files into memory
def load_json_file(path):
    try:
        with open(path) as a:
            data = json.load(a)
        return data
    except FileNotFoundError:
        raise Exception(f"{path} does not exist")

# Converts uuids to names
def uuid_to_display_name(value, category):
    if is_uuid(value):
        data = load_json_file(f"{category}_uuids.json")
        for key in data["data"]:
            if str(key["uuid"]).lower() == str(value).lower():
                return key["displayName"]
        return None
    else:
        return None

# Converts map URL to name
def map_url_to_display_name(value):
    data = load_json_file("map_uuids.json")
    for key in data["data"]:
        if key["mapUrl"] == value:
            return key["displayName"]
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