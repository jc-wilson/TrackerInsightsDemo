function cleanSummary(summary) {
  return summary.replace(/\s*\(low sample\)\.?$/, "").replace(/\.$/, "");
}

function percent(value) {
  return `${Math.round(value * 100)}%`;
}

function gapPoints(insight) {
  return Math.abs(Math.round((insight.win_rate_a - insight.win_rate_b) * 100));
}

function readableStat(stat) {
  return String(stat)
    .replace(/^rounds on /i, "")
    .replace(/^rounds not on /i, "")
    .replace(/^matches on /i, "")
    .replace(/^matches not on /i, "")
    .replace(/^pistol rounds on /i, "")
    .replace(/^eco rounds on /i, "")
    .replace(/^rounds during /i, "")
    .replace(/^matches during /i, "")
    .replace(/^rounds with /i, "")
    .replace(/^matches queued /i, "")
    .replace(/_/g, " ");
}

function sentenceCase(value) {
  const text = String(value);
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function contextName(insight) {
  if (insight.baseline === "matches") {
    return "match";
  }

  if (insight.baseline === "death rounds") {
    return "death-round";
  }

  if (insight.baseline === "pistol rounds") {
    return "pistol-round";
  }

  if (insight.baseline === "eco rounds") {
    return "eco-round";
  }

  if (insight.baseline === "semi-buy rounds") {
    return "semi-buy round";
  }

  if (insight.baseline === "full-buy rounds") {
    return "full-buy round";
  }

  return "round";
}

function targetName(insight) {
  if (insight.group_by === "death_nearest_teammate_distance_bucket") {
    return `Teammates ${readableStat(insight.stat_a).replace(/^death rounds with nearest teammate /i, "")}`;
  }

  if (insight.group_by === "first_death_nearest_teammate_distance_bucket") {
    return `Opening deaths ${readableStat(insight.stat_a).replace(/^opening death rounds with nearest teammate /i, "")}`;
  }

  if (insight.group_by === "vandal vs phantom") {
    return "Vandal";
  }

  if (insight.group_by === "traded death") {
    return "Getting traded";
  }

  if (insight.group_by === "money spent after pistol round win") {
    return sentenceCase(readableStat(insight.stat_a));
  }

  if (insight.group_by === "fast requeue after win vs after loss") {
    return "Fast requeues after wins";
  }

  if (insight.group_by === "took opening duel") {
    return "Opening duels";
  }

  return sentenceCase(readableStat(insight.stat_a || insight.group_by));
}

function comparisonName(insight) {
  if (insight.group_by === "vandal vs phantom") {
    return "Phantom";
  }

  if (insight.group_by === "traded death") {
    return "untraded deaths";
  }

  if (insight.group_by === "money spent after pistol round win") {
    return readableStat(insight.stat_b);
  }

  if (insight.group_by === "fast requeue after win vs after loss") {
    return "fast requeues after losses";
  }

  if (insight.group_by === "took opening duel") {
    return "rounds without the opening duel";
  }

  if (insight.group_by === "map") {
    return "the rest of the map pool";
  }

  if (insight.group_by === "agent") {
    return "the rest of the agent pool";
  }

  if (insight.group_by === "weapon") {
    return "other weapons";
  }

  if (insight.group_by === "armour") {
    return "other armour states";
  }

  if (insight.group_by === "role") {
    return "other roles";
  }

  if (
    insight.group_by === "death_nearest_teammate_distance_bucket"
    || insight.group_by === "first_death_nearest_teammate_distance_bucket"
  ) {
    return "other at-death spacing buckets";
  }

  return readableStat(insight.stat_b || "the comparison group");
}

function statsLine(insight) {
  return `${percent(insight.win_rate_a)} vs ${percent(insight.win_rate_b)}, ${gapPoints(insight)}-point gap`;
}

function phraseGroup(insight) {
  if (insight.group_by === "traded death") {
    return "tradedDeath";
  }

  if (
    insight.group_by === "death_nearest_teammate_distance_bucket"
    || insight.group_by === "first_death_nearest_teammate_distance_bucket"
  ) {
    return "spacing";
  }

  const bank = window.takeawayPhraseBank || {};
  const positive = bank.positive || {};
  const negative = bank.negative || {};

  return positive[insight.group_by] || negative[insight.group_by]
    ? insight.group_by
    : "default";
}

function choose(insight, phrases) {
  const seed = Math.abs(Math.round(insight.z_score * 100)) + targetName(insight).length;
  return phrases[seed % phrases.length];
}

function fillTemplate(template, values) {
  return template.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? "");
}

function buildPhrase(insight) {
  const values = {
    target: targetName(insight),
    comparison: comparisonName(insight),
    context: contextName(insight),
    stats: statsLine(insight),
  };
  const bank = window.takeawayPhraseBank || {};
  const directionBank = insight.significance === "positive" ? bank.positive : bank.negative;
  const phrases = directionBank?.[phraseGroup(insight)] || directionBank?.default || [];
  const phrase = choose(insight, phrases);

  return {
    title: fillTemplate(phrase.title, values),
    action: fillTemplate(phrase.action, values),
  };
}

function buildInsightCopy(insight) {
  const phrase = buildPhrase(insight);

  return {
    title: phrase.title,
    action: phrase.action,
    summary: cleanSummary(insight.summary_text),
  };
}

window.buildInsightCopy = buildInsightCopy;
