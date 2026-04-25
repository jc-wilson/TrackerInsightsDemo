const list = document.querySelector("#insight-list");

function strongestPositive(a, b) {
  return b.z_score - a.z_score;
}

function strongestNegative(a, b) {
  return a.z_score - b.z_score;
}

function formatPercent(value) {
  if (typeof value !== "number") {
    return null;
  }

  return `${Math.round(value * 100)}%`;
}

function metricText(insight) {
  const a = formatPercent(insight.win_rate_a);
  const b = formatPercent(insight.win_rate_b);

  if (!a || !b) {
    return "";
  }

  return ` (${a} vs ${b})`;
}

function renderInsight(insight, index) {
  const copy = buildInsightCopy(insight);
  const item = document.createElement("li");
  const isPositive = insight.significance === "positive";
  item.className = `insight insight--${isPositive ? "positive" : "negative"}`;

  const rank = document.createElement("span");
  rank.className = "insight__rank";
  rank.textContent = String(index + 1).padStart(2, "0");

  const content = document.createElement("div");
  content.className = "insight__content";

  const title = document.createElement("p");
  title.className = "insight__title";
  title.textContent = copy.title;

  const text = document.createElement("p");
  text.className = "insight__text";
  text.textContent = copy.action;

  const metric = metricText(insight);
  if (metric) {
    const metricSpan = document.createElement("span");
    metricSpan.className = "insight__metric";
    metricSpan.textContent = metric;
    text.append(metricSpan);
  }

  const summary = document.createElement("p");
  summary.className = "insight__summary";
  summary.textContent = copy.summary;

  const badge = document.createElement("span");
  badge.className = "insight__badge";
  badge.textContent = isPositive ? "Strength" : "Fix";

  content.append(title, text, summary);
  item.append(rank, content, badge);
  return item;
}

function renderEmptyState() {
  const item = document.createElement("li");
  item.className = "insight insight--empty";
  item.innerHTML = `
    <span class="insight__rank">--</span>
    <div class="insight__content">
      <p class="insight__title">No takeaways available</p>
      <p class="insight__text">No non-low-sample positive or negative insights found in results.json</p>
    </div>
    <span class="insight__badge">Watch</span>
  `;
  list.append(item);
}

async function loadInsights() {
  const response = await fetch("../results.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Could not load results.json (${response.status})`);
  }

  const insights = await response.json();
  const positives = insights
    .filter((insight) => insight.significance === "positive" && !insight.low_sample)
    .sort(strongestPositive)
    .slice(0, 2);

  const negatives = insights
    .filter((insight) => insight.significance === "negative" && !insight.low_sample)
    .sort(strongestNegative)
    .slice(0, 3);

  const selected = [...positives, ...negatives];

  if (!selected.length) {
    renderEmptyState();
    return;
  }

  selected.forEach((insight, index) => {
    list.append(renderInsight(insight, index));
  });
}

loadInsights().catch((error) => {
  console.error(error);
  renderEmptyState();
});
