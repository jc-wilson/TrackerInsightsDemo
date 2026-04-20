import normaliser

for match in normaliser.build_match_rows("match_data.json", "puuid_data.json"):
    print(match)