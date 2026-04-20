from helpers import is_uuid
from helpers import load_json_file

def load_target_puuid(path, index=0):
    puuids = load_json_file(path)
    # Checks if puuids is a list
    if isinstance(puuids, list):
        # Checks if puuids list is empty
        try:
            target_puuid = puuids[index]
            # Validates that the target PUUID is a UUID
            if is_uuid(target_puuid):
                return target_puuid
            else:
                raise Exception("Target PUUID is not a valid UUID")
        except IndexError:
            raise Exception(f"No PUUID found at index {index}")
    else:
        raise Exception("PUUID data is in unexpected format")

def load_match_data(path):
    matches = load_json_file(path)
    # Checks if match data is empty
    if matches:
        # Checks if match data is in the correct format
        if isinstance(matches, list):
            return matches
        else:
            raise Exception("Match Data is in unexpected format.")
    else:
        raise Exception("Match Data is empty.")