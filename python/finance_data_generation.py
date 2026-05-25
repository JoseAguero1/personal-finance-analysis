"""
Personal Finance Analysis — Data Generation & Visualization
============================================================
Portfolio Project: Data Analyst Showcase
Author : Jose
Tools  : Python (pandas, numpy, matplotlib)

Generates a 2-year synthetic personal finance dataset (2023–2024) with:
  - 10 spending categories with monthly budgets
  - Income, expense, and savings transactions
  - Overspend flags for months where category totals exceed budget
  - 3 publication-quality charts for Power BI / website portfolio

Outputs
-------
  finance_transactions.csv      — clean dataset for SQL & Power BI
  chart1_income_vs_expenses.png — grouped bar + net savings line
  chart2_category_vs_budget.png — avg monthly spend vs budget (horizontal bar)
  chart3_spending_trends.png    — monthly trend lines for top 5 categories
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

# ── SEED FOR REPRODUCIBILITY ──────────────────────────────────────────────────
np.random.seed(42)

# ── CONFIG ────────────────────────────────────────────────────────────────────
START_DATE     = "2023-01-01"
END_DATE       = "2024-12-31"
MONTHLY_INCOME = 4500   # fixed monthly salary

# (category, monthly_budget, avg_spend_per_tx, tx_per_month, std_dev)
CATEGORIES = [
    ("Housing",       1400, 1400,  1,  0),
    ("Groceries",      400,   55,  7, 15),
    ("Dining Out",     200,   32,  6, 12),
    ("Transportation", 180,   45,  4, 20),
    ("Utilities",      150,   75,  2, 10),
    ("Healthcare",     100,   85,  1, 30),
    ("Entertainment",  120,   28,  4, 10),
    ("Shopping",       200,   60,  3, 25),
    ("Subscriptions",   80,   15,  5,  2),
    ("Savings",        500,  500,  1,  0),
]

MERCHANTS = {
    "Housing":        ["Oakwood Apartments", "River Bend Rentals", "Metro Property Mgmt"],
    "Groceries":      ["Whole Foods", "Walmart Grocery", "Trader Joe's", "Kroger", "Aldi"],
    "Dining Out":     ["Chick-fil-A", "Chipotle", "Olive Garden", "Local Bistro", "Panda Express", "Starbucks"],
    "Transportation": ["Shell Gas", "BP Gas", "Uber", "Lyft", "City Parking", "Toll Authority"],
    "Utilities":      ["OG&E Electric", "City Water Dept", "AT&T Internet", "ONG Gas"],
    "Healthcare":     ["CVS Pharmacy", "Walgreens", "OU Medical", "Dentist Office", "Eye Care Plus"],
    "Entertainment":  ["AMC Theatres", "Steam Games", "Local Gym", "Bowling Alley", "Concert Hall"],
    "Shopping":       ["Amazon", "Target", "Best Buy", "Nike", "TJ Maxx", "H&M"],
    "Subscriptions":  ["Netflix", "Spotify", "Hulu", "Adobe CC", "Microsoft 365", "YouTube Premium"],
    "Savings":        ["Ally Bank Savings", "Marcus Savings", "Vanguard Transfer"],
}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "ACH Transfer", "Cash"]

# ── PALETTE ───────────────────────────────────────────────────────────────────
BLUE     = "#185FA5"
TEAL     = "#1D9E75"
CORAL    = "#D85A30"
AMBER    = "#BA7517"
GRAY_MID = "#888780"
GRAY_DK  = "#2C2C2A"
BG       = "#FAFAF8"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.facecolor":    BG,
    "figure.facecolor":  BG,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.grid":         True,
    "grid.color":        "#E0DED6",
    "grid.linewidth":    0.5,
    "axes.labelcolor":   GRAY_DK,
    "xtick.color":       GRAY_MID,
    "ytick.color":       GRAY_MID,
    "text.color":        GRAY_DK,
})


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — GENERATE TRANSACTION DATA
# ════════════════════════════════════════════════════════════════════════════

months     = pd.period_range(start=START_DATE, end=END_DATE, freq="M")
month_order = months.strftime("%b %Y").tolist()
rows       = []
tx_id      = 1000

# Income: one paycheck per month
for month in months:
    pay_date = pd.Timestamp(month.to_timestamp()) + pd.offsets.BDay(14)
    rows.append({
        "transaction_id": f"TXN-{tx_id:05d}",
        "date":           pay_date.date(),
        "category":       "Income",
        "subcategory":    "Salary",
        "merchant":       "Employer Direct Deposit",
        "amount":         MONTHLY_INCOME,
        "type":           "Income",
        "payment_method": "ACH Transfer",
        "month":          str(month),
        "year":           month.year,
        "month_num":      month.month,
        "notes":          "Bi-weekly paycheck",
    })
    tx_id += 1

# Expenses: variable transactions per category per month
for month in months:
    month_start = month.to_timestamp()
    month_end   = (month + 1).to_timestamp() - pd.Timedelta(days=1)

    for cat, budget, avg_tx, n_tx, std in CATEGORIES:
        actual_n = max(1, int(np.random.normal(n_tx, 0.5)))

        for _ in range(actual_n):
            tx_date = month_start + pd.Timedelta(
                days=int(np.random.uniform(0, (month_end - month_start).days))
            )
            # Occasional spike to simulate irregular large purchases
            spike = np.random.uniform(1.8, 2.8) if (
                cat not in ("Housing", "Savings") and np.random.random() < 0.07
            ) else 1.0

            amt = avg_tx if std == 0 else max(1, round(np.random.normal(avg_tx, std) * spike, 2))

            rows.append({
                "transaction_id": f"TXN-{tx_id:05d}",
                "date":           tx_date.date(),
                "category":       cat,
                "subcategory":    cat,
                "merchant":       np.random.choice(MERCHANTS[cat]),
                "amount":         amt,
                "type":           "Expense",
                "payment_method": np.random.choice(PAYMENT_METHODS, p=[0.45, 0.35, 0.15, 0.05]),
                "month":          str(month),
                "year":           tx_date.year,
                "month_num":      tx_date.month,
                "notes":          "",
            })
            tx_id += 1

df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
df["month_label"] = pd.to_datetime(df["date"]).dt.strftime("%b %Y")

# ── Flag overspend months ────────────────────────────────────────────────────
budgets     = {c[0]: c[1] for c in CATEGORIES}
expense_df  = df[df["type"] == "Expense"].copy()
monthly_cat = expense_df.groupby(["month", "category"])["amount"].sum().reset_index()
monthly_cat.columns = ["month", "category", "monthly_total"]
monthly_cat["budget"] = monthly_cat["category"].map(budgets)
monthly_cat["overspend_flag"] = monthly_cat["monthly_total"] > monthly_cat["budget"]

overspend_keys = set(
    monthly_cat[monthly_cat["overspend_flag"]][["month", "category"]].apply(tuple, axis=1)
)
df["is_overspend"] = df.apply(
    lambda r: (r["month"], r["category"]) in overspend_keys if r["type"] == "Expense" else False,
    axis=1,
)

df.to_csv("finance_transactions.csv", index=False)
print(f"[1/4] Dataset saved: {len(df):,} rows")


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — CHART 1: Monthly Income vs Expenses + Net Savings Line
# ════════════════════════════════════════════════════════════════════════════

monthly = (
    df.groupby(["month_label", "type"])["amount"]
    .sum()
    .unstack(fill_value=0)
    .reindex([m for m in month_order if m in df["month_label"].unique()])
)
monthly["Net"] = monthly.get("Income", 0) - monthly.get("Expense", 0)

fig, ax = plt.subplots(figsize=(13, 5.2))
x, w = np.arange(len(monthly)), 0.35

ax.bar(x - w/2, monthly["Income"],  width=w, color=TEAL,  alpha=0.88, label="Income",   zorder=3)
ax.bar(x + w/2, monthly["Expense"], width=w, color=CORAL, alpha=0.88, label="Expenses", zorder=3)

ax2 = ax.twinx()
ax2.plot(x, monthly["Net"], color=BLUE, linewidth=2.2, marker="o", markersize=5, label="Net Savings", zorder=4)
ax2.set_ylim(0, monthly["Net"].max() * 2.8)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax2.tick_params(colors=BLUE)
ax2.spines["right"].set(color=BLUE, visible=True)
ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(False)

ax.set_xticks(x)
ax.set_xticklabels(monthly.index, rotation=45, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylabel("Amount ($)")
ax2.set_ylabel("Net Savings ($)", color=BLUE)
ax.set_title("Monthly Income vs. Expenses  ·  2023–2024", fontsize=13, fontweight="500", pad=14)

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", framealpha=0.85, fontsize=9, edgecolor=GRAY_MID)

fig.tight_layout()
fig.savefig("chart1_income_vs_expenses.png", dpi=160, bbox_inches="tight")
plt.close()
print("[2/4] Chart 1 saved")


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — CHART 2: Avg Monthly Spend vs Budget (horizontal bar)
# ════════════════════════════════════════════════════════════════════════════

cat_avg = (
    df[df["type"] == "Expense"]
    .groupby("category")["amount"]
    .sum().div(24).round(2).reset_index()
)
cat_avg.columns = ["category", "avg_monthly"]
cat_avg["budget"] = cat_avg["category"].map(budgets)
cat_avg["over"]   = cat_avg["avg_monthly"] > cat_avg["budget"]
cat_avg = cat_avg.sort_values("avg_monthly", ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
colors = [CORAL if o else TEAL for o in cat_avg["over"]]
ax.barh(cat_avg["category"], cat_avg["avg_monthly"], color=colors, alpha=0.88, height=0.55, zorder=3)
ax.barh(cat_avg["category"], cat_avg["budget"], color="none", edgecolor=GRAY_MID,
        height=0.55, linewidth=1.2, linestyle="--", zorder=4, label="Budget")

for i, (_, row) in enumerate(cat_avg.iterrows()):
    ax.text(row["avg_monthly"] + 6, i, f"${row['avg_monthly']:,.0f}", va="center", fontsize=9)

ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_xlabel("Average Monthly Spend ($)")
ax.set_title("Avg Monthly Spend vs. Budget by Category", fontsize=13, fontweight="500", pad=14)

over_patch  = mpatches.Patch(color=CORAL, alpha=0.88, label="Over budget")
under_patch = mpatches.Patch(color=TEAL,  alpha=0.88, label="Within budget")
budget_line = plt.Line2D([0], [0], color=GRAY_MID, linewidth=1.2, linestyle="--", label="Budget target")
ax.legend(handles=[over_patch, under_patch, budget_line], loc="lower right", fontsize=9,
          framealpha=0.85, edgecolor=GRAY_MID)

fig.tight_layout()
fig.savefig("chart2_category_vs_budget.png", dpi=160, bbox_inches="tight")
plt.close()
print("[3/4] Chart 2 saved")


# ════════════════════════════════════════════════════════════════════════════
# STEP 4 — CHART 3: Monthly Trend Lines — Top 5 Categories
# ════════════════════════════════════════════════════════════════════════════

TOP5         = ["Groceries", "Dining Out", "Shopping", "Transportation", "Entertainment"]
LINE_COLORS  = [BLUE, CORAL, AMBER, TEAL, GRAY_MID]

monthly_cat = (
    df[(df["type"] == "Expense") & (df["category"].isin(TOP5))]
    .groupby(["month_label", "category"])["amount"]
    .sum().unstack(fill_value=0)
    .reindex([m for m in month_order if m in df["month_label"].unique()])
)

fig, ax = plt.subplots(figsize=(13, 5))
x = np.arange(len(monthly_cat))

for cat, color in zip(TOP5, LINE_COLORS):
    if cat in monthly_cat.columns:
        ax.plot(x, monthly_cat[cat], color=color, linewidth=2,
                marker="o", markersize=4, label=cat, zorder=3)

ax.set_xticks(x)
ax.set_xticklabels(monthly_cat.index, rotation=45, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_ylabel("Monthly Spend ($)")
ax.set_title("Monthly Spending Trends — Top 5 Categories", fontsize=13, fontweight="500", pad=14)
ax.legend(loc="upper right", fontsize=9, framealpha=0.85, edgecolor=GRAY_MID)

fig.tight_layout()
fig.savefig("chart3_spending_trends.png", dpi=160, bbox_inches="tight")
plt.close()
print("[4/4] Chart 3 saved")

# ── SUMMARY ──────────────────────────────────────────────────────────────────
total_income   = df[df["type"] == "Income"]["amount"].sum()
total_expenses = df[df["type"] == "Expense"]["amount"].sum()
net_savings    = total_income - total_expenses
savings_rate   = net_savings / total_income * 100

print(f"\n── Portfolio-ready Stats ──────────────────")
print(f"  Total income   : ${total_income:>10,.2f}")
print(f"  Total expenses : ${total_expenses:>10,.2f}")
print(f"  Net savings    : ${net_savings:>10,.2f}  ({savings_rate:.1f}% savings rate)")
print(f"  Overspend txns : {df['is_overspend'].sum()}")
