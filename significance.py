import math

def calculate_win_rate(wins, total):
    if total == 0:
        return 0
    else:
        win_rate = wins / total
        return win_rate

def calculate_standard_error(baseline_rate, sample_size):
    if sample_size == 0:
        return 0
    else:
        standard_error = math.sqrt(baseline_rate * (1 - baseline_rate) / sample_size)
        return standard_error

def calculate_two_group_standard_error(rate_a, total_a, rate_b, total_b):
    if total_a == 0 or total_b == 0:
        return 0
    else:
        variance_a = rate_a * (1 - rate_a) / total_a
        variance_b = rate_b * (1 - rate_b) / total_b
        standard_error = math.sqrt(variance_a + variance_b)
        return standard_error


def calculate_z_score(group_rate, baseline_rate, standard_error):
    if standard_error == 0:
        return 0
    else:
        return (group_rate - baseline_rate) / standard_error

def compare_to_baseline(wins, total, baseline_wins, baseline_total, significance_threshold=1, minimum_sample_size=20):
    win_rate = calculate_win_rate(wins, total)
    baseline_win_rate = calculate_win_rate(baseline_wins, baseline_total)

    standard_error = calculate_standard_error(baseline_win_rate, total)

    z_score = calculate_z_score(win_rate, baseline_win_rate, standard_error)

    if z_score > significance_threshold:
        significance = "positive"
    elif z_score < -significance_threshold:
        significance = "negative"
    else:
        significance = "neutral"

    return {
        "wins": wins,
        "losses": total - wins,
        "sample_size": total,
        "win_rate": win_rate,
        "baseline_win_rate": baseline_win_rate,
        "difference": win_rate - baseline_win_rate,
        "standard_error": standard_error,
        "z_score": z_score,
        "significance": significance,
        "low_sample": total < minimum_sample_size
    }

def compare_two_groups(wins_a, total_a, wins_b, total_b, significance_threshold=1, minimum_sample_size=20):
    win_rate_a = calculate_win_rate(wins_a, total_a)
    win_rate_b = calculate_win_rate(wins_b, total_b)

    standard_error = calculate_two_group_standard_error(win_rate_a, total_a, win_rate_b, total_b)

    z_score = calculate_z_score(win_rate_a, win_rate_b, standard_error)

    if z_score > significance_threshold:
        significance = "positive"
    elif z_score < -significance_threshold:
        significance = "negative"
    else:
        significance = "neutral"

    return {
        "wins_a": wins_a,
        "losses_a": total_a - wins_a,
        "sample_size_a": total_a,
        "win_rate_a": win_rate_a,
        "wins_b": wins_b,
        "losses_b": total_b - wins_b,
        "sample_size_b": total_b,
        "win_rate_b": win_rate_b,
        "difference": win_rate_a - win_rate_b,
        "standard_error": standard_error,
        "z_score": z_score,
        "significance": significance,
        "low_sample": total_a < minimum_sample_size or total_b < minimum_sample_size
    }