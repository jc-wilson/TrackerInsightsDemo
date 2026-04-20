import uuid
import json

def load_json_file(path):
    try:
        with open(path) as a:
            data = json.load(a)
        return data
    except FileNotFoundError:
        raise Exception(f"{path} does not exist")

def uuid_to_display_name(value, category):
    if is_uuid(value):
        data = load_json_file(f"{category}_uuids.json")
        for key in data["data"]:
            if key["uuid"] == str(value).lower():
                return key["displayName"]
        return None
    else:
        return None

def map_url_to_display_name(value):
    data = load_json_file("map_uuids.json")
    for key in data["data"]:
        if key["mapUrl"] == value:
            return key["displayName"]
    return None

def agent_to_role(agent_uuid):
    agent_data = load_json_file("agent_uuids.json")
    for agent in agent_data["data"]:
        if agent["uuid"] == agent_uuid:
            return agent["role"]["displayName"]
    return None

def is_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

def server_normaliser(value):
    if isinstance(value, str):
        server = value.split("-")
        return server[4].capitalize()
    else:
        return None