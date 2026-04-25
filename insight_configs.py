GROUP_INSIGHTS_BY_BASELINE = {
    "matches": [
        "server",
        "map",
        "role",
        "agent",
        "solo_queue",
        "time",
    ],
    "rounds": [
        "server",
        "map",
        "role",
        "agent",
        "solo_queue",
    ],
    "pistol rounds": [
        "map",
        "weapon"
    ],
    "eco rounds": [
        "weapon",
    ],
    "semi-buy rounds": [
        "weapon",
    ],
    "full-buy rounds": [
        "armour",
        "weapon",
    ],
    "death rounds": [
        "death_nearest_teammate_distance_bucket",
    ],
    "opening death rounds": [
        "first_death_nearest_teammate_distance_bucket",
    ],
}


COMPARISON_INSIGHTS = [
    {
        "group_by": "vandal vs phantom",
        "baseline": "rounds",
        "stat_a": "rounds with Vandal",
        "stat_b": "rounds with Phantom",
        "filter_a": lambda row: row["weapon"].lower() == "vandal",
        "filter_b": lambda row: row["weapon"].lower() == "phantom",
    },
    {
        "group_by": "fast requeue after win vs after loss",
        "baseline": "matches",
        "stat_a": "matches queued within 10 minutes of a win",
        "stat_b": "matches queued within 10 minutes of a loss",
        "filter_a": lambda row: row["fast_requeue_after_win"] is True,
        "filter_b": lambda row: row["fast_requeue_after_loss"] is True,
    },
    {
        "group_by": "money spent after pistol round win",
        "baseline": "rounds",
        "stat_a": ">1500 spent in the round after winning pistol round",
        "stat_b": "<=1500 spent in the round after winning pistol round",
        "filter_a": lambda row: row["money_spent_after_pistol_round_win"] is not None and row["money_spent_after_pistol_round_win"] > 1500,
        "filter_b": lambda row: row["money_spent_after_pistol_round_win"] is not None and row["money_spent_after_pistol_round_win"] <= 1500,
    },
    {
        "group_by": "traded death",
        "baseline": "death rounds",
        "stat_a": "rounds in which you were traded within 3 seconds of your death",
        "stat_b": "rounds in which you were not traded within 3 seconds of your death",
        "filter_a": lambda row: row["traded"] is True,
        "filter_b": lambda row: row["traded"] is False,
    },
    {
        "group_by": "took opening duel",
        "baseline": "rounds",
        "stat_a": "rounds in which you took the opening duel",
        "stat_b": "rounds in which you did not take the opening duel",
        "filter_a": lambda row: row["took_opening_duel"] is True,
        "filter_b": lambda row: row["took_opening_duel"] is False,
    },
]

BASELINE_CONFIGS = {
    "rounds": {
        "source": "rounds",
        "filter": lambda row: True,
    },
    "matches": {
        "source": "matches",
        "filter": lambda row: True,
    },
    "pistol rounds": {
        "source": "rounds",
        "filter": lambda row: row["round_number"] in [1, 13],
    },
    "attack rounds": {
        "source": "rounds",
        "filter": lambda row: row["side"] == "Attacker",
    },
    "defense rounds": {
        "source": "rounds",
        "filter": lambda row: row["side"] == "Defender",
    },
    "death rounds": {
        "source": "rounds",
        "filter": lambda row: row.get("deaths", 0) > 0,
    },
    "opening death rounds": {
        "source": "rounds",
        "filter": lambda row: row.get("first_death_nearest_teammate_distance") is not None,
    },
    "eco rounds": {
        "source": "rounds",
        "filter": lambda row: row.get("loadout_value") is not None
                       and row["loadout_value"] <= 1000,
    },
    "semi-buy rounds": {
        "source": "rounds",
        "filter": lambda row: row.get("loadout_value") is not None
                       and 1000 < row["loadout_value"] < 3900,
    },
    "full-buy rounds": {
        "source": "rounds",
        "filter": lambda row: row.get("loadout_value") is not None
                       and row["loadout_value"] >= 3900,
    },
}
